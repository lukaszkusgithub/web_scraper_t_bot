# Web Scrapper
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode
# Telegram Bot
from typing import Final
import logging

from telegram import Update
from telegram.ext import (
	Application,
	CommandHandler,
	ContextTypes,
)

from dotenv import load_dotenv
import os

load_dotenv()

# Enable logging
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')


def save_json_data(data, filename):
	f = '{}.json'.format(filename)
	with open(f, 'w', encoding='utf-8') as f:
		json.dump(data, f)


def open_file(file_name):
	try:
		with open(file_name, "r") as file:
			data = json.load(file)
	except FileNotFoundError:
		print("File not found")
	return data


class WebScraper:
	__olx_offers = []
	__page_number = 1
	__pages_count = 1

	__olx_link = ""
	__data = ""
	__update_json_file = False

	__link_id = 1
	__new_last_id_updated = 0
	__new_last_seen_id = 0
	__html_data = ""
	__end_of_new_offers = 0

	def __init__(self):
		self.__data = open_file("links.json")

	def print_offers(self):
		if len(self.__olx_offers) > 0:
			for item in self.__olx_offers:
				print(item["title"])
				print(item["price"])
				print(item["link"])
				print(item["id"])
				print("\n")

			save_json_data(self.__olx_offers, filename=self.__link_id)

	def get_olx_offers(self, offers, init=False):
		# self.new_last_seen_id = self.data

		for offer in offers:
			olx_offer = {
				'link': "",
				'title': "",
				'price': "",
				'id': "",
			}

			title = offer.find('h6', 'css-16v5mdi er34gjf0')
			price = offer.find('p', 'css-10b0gli er34gjf0')
			link = offer.find('a', 'css-rc5s2u')
			new_offer = offer.find('p', 'css-1kyngsx er34gjf0')
			offer_id = offer['id']

			if price is not None:
				price = " ".join(re.split('(zł)', price.text))
				olx_offer["price"] = price
			if title is not None:
				olx_offer["title"] = title.text
			if link is not None:
				olx_offer["link"] = "https://www.olx.pl" + link['href']

			olx_offer["id"] = offer_id

			if new_offer is not None:
				if self.__page_number == 1 and self.__new_last_id_updated == 0:
					self.__new_last_seen_id = offer_id
					self.__new_last_id_updated = 1
					if init:
						break
			else:
				self.__end_of_new_offers = 1
				break

			self.__olx_offers.append(olx_offer)

	def find_offers(self, init=False):
		offers = self.__html_data.select("div[data-cy=l-card]")
		self.get_olx_offers(offers, init)

	def change_sorting_type(self):
		parsed_url = urlparse(self.__olx_link)

		query_params = parse_qs(parsed_url.query)
		search_order = "created_at:desc"
		query_params["search[order]"] = [search_order]

		updated_query_string = urlencode(query_params, doseq=True)

		self.__olx_link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{updated_query_string}"

	def update_last_seen_id(self):

		parsed_url = urlparse(self.__olx_link)
		query_params = parse_qs(parsed_url.query)

		if "last_seen_id" in query_params:
			last_seen_id = query_params["last_seen_id"][0]
			self.__olx_link = self.__olx_link.replace("last_seen_id=" + str(last_seen_id),
			                                          "last_seen_id=" + str(self.__new_last_seen_id))
		else:
			self.__olx_link += "&last_seen_id=" + str(self.__new_last_seen_id)

	def update_page(self):
		parsed_url = urlparse(self.__olx_link)
		query_params = parse_qs(parsed_url.query)

		if "page" in query_params:
			last_page = query_params["page"][0]
			self.__olx_link = self.__olx_link.replace("page=" + str(last_page), "page=" + str(self.__page_number))
		else:
			self.__olx_link += "&page=" + str(1)

	def init_scanning(self):
		self.__olx_link = self.__data["{}".format(self.__link_id)]["link"]
		self.change_sorting_type()
		self.update_last_seen_id()

		page = requests.get(self.__olx_link)
		self.__html_data = BeautifulSoup(page.text, 'html.parser')

		self.find_offers(init=True)

		self.update_last_seen_id()

		self.__data["{}".format(self.__link_id)]["link"] = self.__olx_link
		self.__data["{}".format(self.__link_id)]["last_seen_id"] = self.__new_last_seen_id

	def run_scanning(self):
		self.__new_last_seen_id = self.__data["{}".format(self.__link_id)]["last_seen_id"]
		# print(self.__new_last_seen_id)

		page = requests.get(self.__olx_link)
		self.__html_data = BeautifulSoup(page.text, 'html.parser')

		while True:
			if self.__page_number != 1:
				self.update_page()
				page = requests.get(self.__olx_link)
				self.__html_data = BeautifulSoup(page.text, 'html.parser')
			elif self.__page_number == 1:
				self.update_page()
				pagination_list = self.__html_data.select("ul[data-testid=pagination-list]")
				if pagination_list is not None:
					if len(pagination_list) > 0:
						pagination = pagination_list[0].findAll('li')
						self.__pages_count = pagination[-1].text

			self.find_offers()

			self.print_offers()

			if self.__end_of_new_offers:
				print("END of new Offers")
				break

			if self.__page_number == int(self.__pages_count):
				print("END of pages")
				break

			self.__page_number = self.__page_number + 1

		self.update_last_seen_id()
		self.__data["{}".format(self.__link_id)]["link"] = self.__olx_link
		self.__data["{}".format(self.__link_id)]["last_seen_id"] = self.__new_last_seen_id

	def main_loop(self):
		self.__olx_offers = []
		if len(self.__data) > 0:
			link_max_number = len(self.__data)

			for i in range(1, link_max_number + 1):
				print(f"Link {i}")
				self.__link_id = i
				self.__olx_link = self.__data["{}".format(i)]["link"]
				self.__page_number = 1

				# init scanning
				if self.__data["{}".format(i)]["init"] == 1:
					self.init_scanning()
					self.__data["{}".format(i)]["init"] = 0

				# scan for offers
				self.run_scanning()
			# self.__update_json_file = True

			# if self.__update_json_file:
			save_json_data(self.__data, "links")

	def get_offers(self):
		return self.__olx_offers


async def start_scanning():
	print("Schedule pending")
	web_scrapper = WebScraper()
	web_scrapper.main_loop()
	return web_scrapper.get_offers()


async def check_offers(context: ContextTypes.DEFAULT_TYPE):
	offers = await start_scanning()
	text = ""
	if len(offers) > 0:
		for offer in offers:
			text += offer['title'] + "\n"
			text += offer['price'] + "\n"
			text += offer['link'] + "\n\n"
			await context.bot.send_message(chat_id=context.job.chat_id, text=text)
			text = ""

		text = "End of new Offers"
		await context.bot.send_message(chat_id=context.job.chat_id, text=text)


async def callback_scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):
	chat_id = update.message.chat_id
	name = update.effective_chat.full_name
	await context.bot.send_message(chat_id=chat_id, text='Start scanner')
	context.job_queue.run_repeating(check_offers, 10, data=name, chat_id=chat_id)


def main() -> None:
	"""Run bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(TOKEN).build()

	scanner_handler = CommandHandler('start', callback_scanner)
	application.add_handler(scanner_handler)

	# Run the bot until the user presses Ctrl-C
	print("Bot polling")
	application.run_polling()


if __name__ == "__main__":
	main()
