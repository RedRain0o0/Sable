# Sable Rewrite V1.0

import os, json, random
from datetime import datetime
from discord import Client, Member, Intents, Game, Message, MessageType, Thread, Embed
from dotenv import load_dotenv
from typing import List

# Bot setup
client = Client(intents=Intents.all(), activity=Game(name='with your mind~'))

# .env setup
load_dotenv("../config/.env")
TOKEN = os.getenv('TOKEN')

# Functions

client.run(TOKEN)