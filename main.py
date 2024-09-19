import os
import os.path
import io
import discord
import asyncio
import setproctitle
import psutil
from io import BytesIO
from pprint import pprint

import logging
logging.basicConfig(level=logging.INFO)

import nest_asyncio
nest_asyncio.apply()

client = discord.Client()

dict = {}

base = []
letters = ["a", "b", "c", "ç", "d", "e", "f", "g", "ğ", "h", "i", "ı", "j", "k", "l", "m", "n", "o", "ö", "p", "r", "s", "ş", "t", "u", "ü", "v", "q", "w", "x", "z", "y", "z"]
symbols = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ",", ":", ";", '"', "'", "!", "?", "(", ")", "+", "-", "_", "/", "*", "$", "&", "%", "{", "}", "=", "#", "<", ">", "^", "\n"]

def decimalToBinary(n):
    return bin(n).replace("0b", "")

def binaryToDecimal(n):
	return int(n, 2)

def decode(code):
	i = 0
	cur_let = 1

	output = {}

	for ii in range(int(len(code)/8)):
		ii = ii + 1
		output[str(ii)] = ""

	for bit in code:
		if i == 8:
			cur_let = cur_let + 1
			i = 0
		output[str(cur_let)] = output[str(cur_let)] + bit
		i = i + 1
	
	result = ""

	for key, value in output.items():
		result = result + base[binaryToDecimal(value)-1]

	return result

def encode(text):
	result = ""

	for char in text:
		if char not in dict.keys():
			continue
		decimal = dict[char]
		binary = decimalToBinary(decimal)
		newbinary = ""
		if 8 - len(binary) != 0:
			test = 8 - len(binary)
			for _ in range(test):
				newbinary = newbinary + "0"
			newbinary = newbinary + binary
		else:
			newbinary = binary
		result = result + newbinary

	return result

@client.event
async def on_message(message):
	if message.author.id == client.user.id:
		return

	sender = message.author

	if sender.bot:
		return
	
	if message.attachments:
		if "!encode" in message.content or "!ec" in message.content:
			for a in message.attachments:
				content = await a.read()
				await message.reply(file=discord.File(fp=io.StringIO(encode(str(content.decode("UTF-8")))), filename="code.txt"))
		elif "!decode" in message.content or "!dc" in message.content:
			for a in message.attachments:
				content = await a.read()
				await message.reply(file=discord.File(fp=io.StringIO(decode(str(content.decode("UTF-8")))), filename="code.txt"))
		return

	if message.content[:1] == "!":
		body = message.content[1:].split(None, 1)

		if body == "":
			return

		cmd = body[0]

		content = ""
		args = []

		if len(body) == 2:
			content = body[1]
			args = content.split()

		if cmd == "encode" or cmd == "ec":
			if content == "":
				await message.reply("şifrelenmesi için bir şey yaz")
				return
			await message.reply(file=discord.File(fp=io.StringIO(encode(str(content))), filename="code.txt"))

		if cmd == "decode" or cmd == "dc":
			if content == "":
				await message.reply("çözümlenmesi için bir şey yaz")
				return
			await message.reply(file=discord.File(fp=io.StringIO(decode(str(content))), filename="code.txt"))

async def main():
	global dict, base

	loop = asyncio.get_event_loop()
	
	i = 1

	for letter in letters:
		dict[letter] = i
		base.append(letter)
		i = i + 1
		dict[letter.upper()] = i
		base.append(letter.upper())
		i = i + 1

	for letter in symbols:
		dict[letter] = i
		base.append(letter)
		i = i + 1

	print("starting discord client")
	loop.create_task(client.start(os.getenv("TOKEN")))

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		await client.close()
	finally:
		await client.close()

def is_process_running(name):
	for process in psutil.process_iter(['name']):
		if process.info['name'] == name:
			return True
	return False

if __name__ == "__main__":
	if is_process_running('cryptor'):
		print("already running")
	else:
		setproctitle.setproctitle('wordgen')
		asyncio.run(main())
