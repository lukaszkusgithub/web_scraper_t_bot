# Telegram bot sniper OLX

This is a Telegram bot designed to monitor and snipe deals on OLX. The bot allows you to configure specific search links and receive notifications when new items are listed matching your criteria. By quickly responding to these notifications, you can increase your chances of securing the deals before others.

## Configuration
Before using the Telegram bot sniper for OLX, you need to configure two files: `links.json` and `.env`.

### `links.json`
The `links.json` file is used to define the search links and their associated settings. The structure of the file should be as follows:
```json
{
  "1": {
    "title": "name",
    "link": "",
    "init": 1,
    "last_seen_id": "0"
  },
  "2": {
    "title": "name",
    "link": "",
    "init": 1,
    "last_seen_id": "0"
  },
  "3": {
    "title": "name",
    "link": "",
    "init": 1,
    "last_seen_id": "0"
  }
}
```

You can define multiple search links by adding additional numbered objects within the curly braces. Each link should have the following properties:

* **"title"**: A descriptive name for the search link.
* **"link"**: The URL of the OLX search link.
* **"init"**: Initial value (1 or 0) indicating whether the link is new or 
  not. Leave it as "1"
* **"last_seen_id"**: The ID of the last item seen for the link. Leave it as 
  "0" 
initially. <br><br>
Make sure to replace the empty strings with the appropriate values for the 
`"link"` property.

### `.env`
The `.env` file is used to store sensitive information, such as the bot token and username. Create a new file named .env and define the following variables:

```
TOKEN=""
BOT_USERNAME=""
```

Obtain the bot token from the BotFather on Telegram and assign it to the **TOKEN** variable. Set the **BOT_USERNAME** variable to the username chosen for your bot.

## Usage
Once you have configured the `links.json` and `.env` files, you can run the 
Telegram bot sniper for OLX. Start the bot and interact with it on Telegram to receive notifications about new listings matching your configured search links.

Feel free to modify the `links.json` file whenever you want to add, remove, or update the search links. Restart the bot after making changes for the new configuration to take effect.

Please note that this Telegram bot sniper for OLX is provided as-is and may require additional customization or enhancements to suit your specific needs.

**Disclaimer**: Use this bot responsibly and in compliance with OLX's terms of 
service.