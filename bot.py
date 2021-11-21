import sqlite3
from sqlite3 import Error
import discord
import discord.client
import logging
import datetime
import sys
from decouple import config
from discord.ext import tasks as discordTasks
import amazonNews



#setting up logger
logging.basicConfig(filename='./logs/bot.log',level=logging.INFO)
logging.info(datetime.datetime.utcnow().isoformat())
logging.info('Logging initialized successfully')

# Hijack output to logger
class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, log_level=logging.INFO):
		self.logger = logger
		self.log_level = log_level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

	def flush(self):
		pass

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl




#all times are shifted to est

def create_connection(db_file):
	conn = None
	try:
		conn = sqlite3.connect('AGNewsBot.db')
	except Error as e:
		logging.error(e)

	return conn


def create_links_db(conn):
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS LINKS 
	([id] INTEGER PRIMARY KEY, [link] str)''')
	conn.commit()
	return

def create_channel_db(conn):
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS CHANNELS
	([id] INTEGER PRIMARY KEY, [channel id] integer)''')
	conn.commit()
	return

def query_channels(conn,channel_id):
	c = conn.cursor()
	rows = 'None'
	try:
		c.execute('SELECT * FROM CHANNELS WHERE [channel id] == ?',(channel_id,))
		rows = c.fetchone()
	except Error as e:
		logging.info(e)
	return rows

def create_channel(conn,channel_id):
	c = conn.cursor()
	rows = []
	c.execute('SELECT * FROM CHANNELS WHERE [channel id] == ?',(channel_id,))
	rows = c.fetchall()
	if rows == []:
		c.execute('INSERT INTO CHANNELS VALUES (?,?)',(None,channel_id))
		conn.commit()
	return

def create_link(conn, linkText):
	c = conn.cursor()
	rows = []
	c.execute('SELECT * FROM LINKS WHERE [link] == ?',(linkText,))
	rows = c.fetchall()
	if rows == []:
		c.execute('INSERT INTO LINKS VALUES (?,?)',(None,linkText))
		conn.commit()
	return

def delete_channel(conn, channel_id):
	c = conn.cursor()
	c.execute("DELETE FROM CHANNELS WHERE [channel id] == ?",(channel_id,))
	conn.commit()

def query_links(conn):
	c = conn.cursor()
	rows = 'None'
	try:
		c.execute('SELECT * FROM LINKS')
		rows = c.fetchone()
	except Error as e:
		logging.info(e)
	return rows

def query_channel(conn):
	c = conn.cursor()
	rows = 'None'
	try:
		c.execute('SELECT * FROM CHANNELS')
		rows = c.fetchone()
	except Error as e:
		logging.info(e)
	return rows

def update_link(conn,linkText,primaryKey):
	c = conn.cursor()
	c.execute('UPDATE LINKS SET [link] = ? WHERE [id] == ?',(linkText,primaryKey))
	conn.commit()





# @client.event
# async def on_reaction_add(reaction,user):
# 	conn = sqlite3.connect('users.db')
# 	rows = query_user(conn,user.id)
# 	if rows[1] == user.id and rows[3] == reaction.message.id:
# 		update_user_id(conn,user.id,2)
	

def botFunc():
	#sql setup
	global conn
	conn = sqlite3.connect('AGNewsBot.db')
	create_links_db(conn)
	create_channel_db(conn)
	#discord setup
	TOKEN = config('TOKEN')
	botPrefix = config('PREFIX')
	client = discord.Client()

	

	@client.event
	async def on_ready():
		logging.info('Logged in as')
		logging.info(client.user.name)
		logging.info(client.user.id)
		logging.info('------')


	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		elif(message.content.lower().startswith(botPrefix + "help")):
			await message.channel.send("```" + botPrefix + '''add channel: add this channel to the list of channels which will recieve a message whenever a new article is added to https://www.newworld.com/en-us/news
This role requires the 'server manager' permission.```
```''' + botPrefix + '''remove channel: remove this channel from list of channels to recieve messages.
This role requires the 'server manager' permission```''')

		elif(message.author.guild_permissions.manage_guild):
			#only allows those with the 'server manager' permission to use command
			if message.content.lower().startswith(botPrefix + "add channel"):
				create_channel(conn, message.channel.id)
				logging.info('channel id = ' + str(message.channel.id))

			elif message.content.lower().startswith(botPrefix + "remove channel"):
				delete_channel(conn, message.channel.id)



	@discordTasks.loop(minutes=1.0)
	async def newsMessanger():
		global conn
		NewsURL = amazonNews.main()
		response = NewsURL
		linksData = query_links(conn)
		if(str(linksData) == 'None'):
			create_link(conn, str(NewsURL))
		elif(linksData[1] != NewsURL):
			update_link(conn,NewsURL,1)
			await client.wait_until_ready()
			channelQuery = query_channel(conn)
			for i in range(int(len(channelQuery)/2)):
				channel = client.get_channel(channelQuery[(i*2)+1])
				await channel.send(response)



	try:
		newsMessanger.start()
		client.run(TOKEN)
	except Exception as e:
		logging.exception('In-loop exception:')



if __name__ == '__main__':
	botFunc()
