# Amazon-Games-Discord-News
A discord bot that posts a message whenever a new article is added by amazon games to https://www.newworld.com/en-us/news. This is meant to supplement the AG discord announcements which typically do not include their news articles.
Prerequsites: Python (made in version 3.7.4) and python libraries bs4, sqlite3, discord.py, and python-decouple

To use the bot, edit the file '.env' and insert the token and prefix for the bot to use
Ex:
TOKEN=longStringOfCharacters
PREFIX=!

To get a token for the bot, go to https://discord.com/developers/applications


Then, run bot.py in python