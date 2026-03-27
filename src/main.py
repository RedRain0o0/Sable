# Sable Rewrite V1.0

import ast, codecs, json, logging, os, sqlite3, random, re
from datetime import datetime
from discord import Client, Embed, Game, Guild, Intents, Member, Message, MessageType, Thread
from discord.utils import MISSING
from dotenv import load_dotenv
from pathlib import Path
from tsf_decoder import *
from typing import List

# Setup
client = Client(intents=Intents.all(), activity=Game(name='with the code'))

# .env
load_dotenv("../config/.env")
TOKEN = os.getenv('TOKEN')
LOG_PATH = os.getenv('LOG_PATH')
DATABASE_PATH = os.getenv('DATABASE_PATH')
ATTACHMENTS_PATH = os.getenv('ATTACHMENTS_PATH')
REPLY_TYPE = os.getenv('REPLY_TYPE')
ADMINS = os.getenv('ADMINS')
WEBHOOK_NAME = os.getenv('WEBHOOK_NAME')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')

# Attachments
if not os.path.exists(ATTACHMENTS_PATH):
  os.makedirs(ATTACHMENTS_PATH)

# sqlite
database_exists = False
if not os.path.exists(DATABASE_PATH):
  os.makedirs(DATABASE_PATH)
if Path(f"{DATABASE_PATH}/servers.db").is_file(): database_exists = True
database_connection = sqlite3.connect(f"{DATABASE_PATH}/servers.db")
database_cursor = database_connection.cursor()
if not database_exists:
  transformation_specs = """UserID int NOT NULL,
  GuildID int NOT NULL,
  Name varchar(255) NOT NULL,
  Avatar text NOT NULL,
  TextModifiers int NOT NULL,
  StutterChance float(10) NOT NULL,
  Pronouns text,
  Biography text, 
  Story text,
  FallbackPrefix text,
  FallbackSuffix text,
  FallbackMuffle text,
  FallbackAltMuffle text,
  Prefixes text NOT NULL,
  Suffixes text NOT NULL,
  Sprinkles text NOT NULL,
  Muffles text NOT NULL,
  AltMuffles text NOT NULL,
  Censors text NOT NULL,
  Triggers text NOT NULL,
  AltTriggers text NOT NULL"""
  database_cursor.execute("CREATE TABLE GuildConfig(GuildID int PRIMARY KEY, BlockedChannels text, SableAdminRoleID int, AnnoucementsChannel int, AllForce bool, BotHasSwapPerms bool, BotAutoConsents bool, BotResponses bool, BotPersonality varchar(255))")
  database_cursor.execute("CREATE TABLE Consents(MessageID int PRIMARY KEY, User1ID int, User2ID int)")
  database_cursor.execute("CREATE TABLE MessageIDs(ResultID int PRIMARY KEY, MemberID int NOT NULL, ChannelID int NOT NULL, ThreadID int)")
  database_cursor.execute(f"CREATE TABLE Transformations({transformation_specs})")
  database_cursor.execute(f"CREATE TABLE TransformationCache({transformation_specs})")
  database_cursor.execute(f"CREATE TABLE TransformationHolding({transformation_specs})")
database_connection.commit()

# logging
if not os.path.exists(LOG_PATH):
  os.makedirs(LOG_PATH)
last_log_time = ""
if Path(f"{LOG_PATH}/.time").is_file():
  with open(f"{LOG_PATH}/.time", "r") as f:
    last_log_time = f.read()
with open(f"{LOG_PATH}/.time", "w") as f:
  f.write(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
if Path(f"{LOG_PATH}/latest.log").is_file(): os.rename(f"{LOG_PATH}/latest.log", f"{LOG_PATH}/{last_log_time}.log")
logger = logging.getLogger("sable.main")
logging.basicConfig(filename=f"{LOG_PATH}/latest.log", level=logging.INFO, format='%(asctime)s %(levelname)-9s%(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w')

# Functions
def database_command(command: str, args):
  database_cursor.execute(command,args)
  database_connection.commit()

def database_check_exists(table: str, where: str):
  database_cursor.execute(f"""SELECT EXISTS(SELECT 1 FROM {table} WHERE {where});""")
  if database_cursor.fetchone()[0] == 1: return True
  else: return False

def database_fetch_value(column: str, table: str, where: str):
  database_cursor.execute(f"""SELECT {column} FROM {table} WHERE {where};""")
  return database_cursor.fetchone()[0]

async def is_admin(message: Message):
  author_id = message.author.id
  dotenv_admin = str(author_id) in ADMINS
  guild_owner = author_id == message.guild.owner.id
  sable_admin = False
  if database_check_exists("GuildConfig", f"GuildID={message.guild.id}"):
    sable_admin_role = await message.guild.fetch_role(database_fetch_value("SableAdminRoleID", "GuildConfig", f"GuildID={message.guild.id}"))
    if sable_admin_role in message.author.roles:
      sable_admin = True
  return dotenv_admin or guild_owner or sable_admin

async def can_user_run_command(message: Message):
  is_allow_all_force_enabled = False
  if database_check_exists("GuildConfig", f"GuildID + {message.guild.id}"):
    if database_fetch_value("AllForce", "GuildConfig", f"GuildID={message.guild.id}") == 1:
      is_allow_all_force_enabled = True
  return await is_admin(message) or is_allow_all_force_enabled

def get_flags(args: str):
  flags = []
  for arg in args:
    if arg.startswith("-"):
      flags.append(arg)
  return flags

def dialogue(message: Message, dialogue_id: str):
  return dialogue_id

def channel_blacklisted(message: Message):
  try:
    return message.channel.id in ast.literal_eval(database_fetch_value("BlockedChannels", "GuildConfig", f"GuildID={message.guild.id}"))
  except:
    return False

# Source - https://stackoverflow.com/a/43789171
# Posted by roskakori, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-25, License - CC BY-SA 3.0

#: BOMs to indicate that a file is a text file even if it contains zero bytes.
_TEXT_BOMS = (
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF8,
)

def is_binary_file(source_path):
    with open(source_path, 'rb') as source_file:
        initial_bytes = source_file.read(8192)
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) \
           and b'\0' in initial_bytes

def apply_speech(content: str, memberid: int, guildid: int):
  where = f"UserID={memberid} AND GuildID={guildid}"

  # Alt Muffles
  alt_muffles = ast.literal_eval(database_fetch_value("AltMuffles", "Transformations", where))
  fallback_alt_muffle = database_fetch_value("FallbackAltMuffle", "Transformations", where)
  for alt_muffle in alt_muffles:
    if (random.random() * 100) <= float(alt_muffle[1]):
      fallback_alt_muffle = alt_muffle[0]
      break
  if fallback_alt_muffle != None and fallback_alt_muffle != "":
    return fallback_alt_muffle
  
  # Alt Triggers
  alt_triggers = ast.literal_eval(database_fetch_value("AltTriggers", "Transformations", where))
  alt_trigger_send = None
  for alt_trigger in alt_triggers:
    if content.lower().find(alt_trigger[0]) > -1:
      alt_trigger_send = alt_trigger[1]
      break
  if alt_trigger_send != None and alt_trigger_send != "":
    return alt_trigger_send

  # Prefix
  append_prefix = ""
  prefixes = ast.literal_eval(database_fetch_value("Prefixes", "Transformations", where))
  fallback_prefix = database_fetch_value("FallbackPrefix", "Transformations", where)
  if fallback_prefix != None and fallback_prefix != "":
    append_prefix = fallback_prefix
    for prefix in prefixes:
      if (random.random() * 100) <= float(prefix[1]):
        append_prefix = prefix[0]
        break
  else:
    for prefix in prefixes:
      if (random.random() * 100) <= float(prefix[1]):
        append_prefix += prefix[0]
  small_text = content.split()[0].startswith("-#")
  if small_text:
    append_prefix += "\n"
  
  # Suffix
  prepend_suffix = ""
  suffixes = ast.literal_eval(database_fetch_value("Suffixes", "Transformations", where))
  fallback_suffix = database_fetch_value("FallbackSuffix", "Transformations", where)
  if fallback_suffix != None and fallback_suffix != "":
    prepend_suffix = fallback_suffix
    for suffix in suffixes:
      if (random.random() * 100) <= float(suffix[1]):
        prepend_suffix = suffix[0]
        break
  else:
    for suffix in suffixes:
      if (random.random() * 100) <= float(suffix[1]):
        prepend_suffix += suffix[0]
  small_text = content.splitlines()[-1].startswith("-#")
  if small_text:
    prepend_suffix = "\n" + prepend_suffix
  
  # Sprinkles
  sprinkles = ast.literal_eval(database_fetch_value("Sprinkles", "Transformations", where))
  words = content.split()
  temp_list = []
  for word in words:
    temp_list.append(f" {word}")
    for sprinkle in sprinkles:
      if (random.random() * 100) <= float(sprinkle[1]):
        temp_list.append(sprinkle[0])
        break
  content = ''.join(temp_list)

  # Muffles
  muffles = ast.literal_eval(database_fetch_value("Muffles", "Transformations", where))
  fallback_muffle = database_fetch_value("FallbackMuffle", "Transformations", where)
  words = content.split()
  temp_list = []
  for word in words:
    muffled = False
    key = re.sub(r'[^\w\s]', '', word)
    for muffle in muffles:
      if (random.random() * 100) <= float(muffle[1]):
        replacement = muffle[0]
        if key.istitle():
          replacement = muffle[0].title()
        if key.isupper():
          replacement = muffle[0].upper()
        word = word.lower().replace(key.lower(), replacement)
        muffled = True
        break
    if not muffled:
      if fallback_muffle != None and fallback_muffle != "":
        replacement = fallback_muffle
        if key.istitle():
          replacement = fallback_muffle.title()
        if key.isupper():
          replacement = fallback_muffle.upper()
        word = word.lower().replace(key.lower(), replacement)
    temp_list.append(word)
  content = ' '.join(temp_list)

  # Censors
  censors = ast.literal_eval(database_fetch_value("Censors", "Transformations", where))
  words = content.split()
  temp_list = []
  for word in words:
    key = re.sub(r'[^\w\s]', '', word)
    for censor in censors:
      if key.lower() == censor[0]:
        replacement = censor[1]
        if key.istitle():
          replacement = censor[1].title()
        if key.isupper():
          replacement = censor[1].upper()
        word = word.lower().replace(key.lower(), replacement)
    temp_list.append(word)
  content = ' '.join(temp_list)

  # Triggers
  is_triggered = False
  triggers = ast.literal_eval(database_fetch_value("Triggers", "Transformations", where))
  lowest_trigger = len(content)+1
  prepend_trigger = ""
  for trigger in triggers:
    size = content.lower().find(trigger[0])
    if size >= 0 and size < lowest_trigger:
      lowest_trigger = size
      prepend_trigger = trigger[1]
      is_triggered = True
  content = content[0:lowest_trigger]

  # Stutter
  stutter_chance = database_fetch_value("StutterChance", "Transformations", where)
  words = content.split()
  temp_list = []
  for word in words:
    if (random.random() * 100) <= float(stutter_chance):
      word = word[0:1] + "-" + word
    temp_list.append(word)
  content = ' '.join(temp_list)

  return append_prefix + content + ((" "+prepend_trigger) if is_triggered else prepend_suffix)

def check_is_user_is_transformed(guild: Guild, member: Member):
  return database_check_exists("Transformations", f"UserID = {member.id} AND GuildID={guild.id}") or database_check_exists("Transformations", f"UserID={member.id} AND GuildID=0")

def reply_embed(message: Message):
  referenced = message.reference.resolved
  if len(referenced.content) > 100:
    preview = referenced.content[:97]
    reference = referenced.content[97:]
    print(preview)
    print(reference)
    if preview.count("||") % 2 and reference.count("||") % 2:
      preview += "||"
    # TODO: Add more markup support
  else:
    preview = referenced.content
  
  if isinstance(referenced, Message):
    if isinstance(referenced.author, Member):
      embed = Embed(
        description = f'[Reply]({referenced.jump_url})\n{preview}',
        timestamp = referenced.created_at,
        color = referenced.author.color
      )
    else:
      embed = Embed(
        description = f'[Reply]({referenced.jump_url})\n{preview}',
        timestamp = referenced.created_at,
        color = 0xffffff
      )
    embed.set_author(
      name = referenced.author.display_name,
      icon_url = referenced.author.display_avatar.url,
      url = f"https://discord.com/users/{referenced.author.id}"
    )
  else:
    embed = Embed(
      title = "__Reply/Forward__",
      description = "Original Message Not Found.",
      color = 0x2480ee
    )
    logger.error(f'Replying/Forwarding: Original Message Not Found.')
  return embed

def reply_transformate(message: Message): # TODO: fix this being not working
  referenced = message.reference.resolved
  reply = "***Replying to "
  if referenced.webhook_id == None:
    reply += f"<@{referenced.author.id}>"
  else:
    if database_check_exists("MessageIDs" f"ResultID={referenced.id}"):
      reply += f"<@{database_fetch_value("MemberID", "MessageIDs", f"ResultID={referenced.id}")}>"
    else:
      reply += "`NOT FOUND`"
  reply += " on "
  reply += f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{referenced.id}"
  reply += ":***\n"
  return reply

async def fake_commands(message: Message):
  # Bypass commands
  if message.content.startswith("\\"): # Bypass proxy
    return True
  elif message.content.startswith("pk;"): # Ignore PluralKit commands
    return True
  elif message.content.startswith("tul!"): # Ignore TupperBox commands
    return True
  
  command = message.content.split(' ', 1)[0]
  
  match command:
    # Server Commands
    case "sb!setup-server": # Setup server config
      if not await is_admin(message): return True
      logger.info(f"Setting up config for server {message.guild.id}...")
      args = message.content.split(' ')
      
      try:
        if not args[6] in ['sub', 'dom', 'rob', 'ran']:
          raise Exception("Must be one of 'sub', 'dom', 'rob', or 'ran'")
        sable_admin_exists = False
        for role in message.guild.roles:
          if role.name == "Sable Admin":
            sable_admin_exists = True
        if not sable_admin_exists:
          await message.guild.create_role(name = "Sable Admin", reason = "Required for Swap-Bot")
        sable_admin_role = None
        for role in message.guild.roles:
          if role.name == "Sable Admin":
            sable_admin_role = role
        database_command(f"""
          INSERT INTO GuildConfig
          VALUES ({message.guild.id},
          '[]',
          {sable_admin_role.id},
          ?, ?, ?, ?, ?, ?);""",
          (args[1],
          args[2],
          args[3],
          args[4],
          args[5],
          args[6]))
        await message.add_reaction("✅")
        logger.info("Success")
        
      except sqlite3.IntegrityError:
        await message.add_reaction("❗")
        await message.reply(f'Config already exists for {message.guild.id}, proceed?')
        logger.info("Config already exists for server")
        
      except Exception as e:
        await message.add_reaction("❌")
        await message.channel.send(f'<insert proper use of command>')
        logger.error(e)
        logger.info("Failed to create config")
        
      return True
    
    case "sb!confirm-reset": # Confirm server config reset
      if not await is_admin(message): return True
      logger.info(f"Overwriting config for {message.guild.id}...")
      referenced = message.reference.resolved
      
      if referenced.content == f'Config already exists for {message.guild.id}, proceed?':
        args = await referenced.fetch()
        args = args.reference.resolved.content.split(' ')
        sable_admin_exists = False
        for role in message.guild.roles:
          if role.name == "Sable Admin":
            sable_admin_exists = True
        if not sable_admin_exists:
          await message.guild.create_role(name = "Sable Admin", reason = "Required for Swap-Bot")
        sable_admin_role = None
        for role in message.guild.roles:
          if role.name == "Sable Admin":
            sable_admin_role = role
        database_command(f"""
          UPDATE GuildConfig 
          SET BlockedChannels = '[]',
          SableAdminRoleID = {sable_admin_role.id},
          AnnoucementsChannel = ?,
          AllForce = ?,
          BotHasSwapPerms = ?,
          BotAutoConsents = ?,
          BotResponses = ?,
          BotPersonality = ?
          WHERE GuildID = {message.guild.id};""", (
          args[1],
          args[2],
          args[3],
          args[4],
          args[5],
          args[6]
          ))
        await message.add_reaction("✅")
        
      return True
    
    case "sb!blacklist": # Blacklist current or specified channel
      try:
        message_content = message.content
        message_channel_id = message.channel.id
        blocked_channels = ast.literal_eval(database_fetch_value("BlockedChannels", "GuildConfig", f"GuildID={message.guild.id}"))
        if message_content.startswith("sb!blacklist "): 
          content = message_content.removeprefix('sb!blacklist ')
        else:
          if not message_channel_id in blocked_channels:
            blocked_channels.append(message_channel_id)
            await message.channel.send(dialogue(message, 'blacklist'))
            await message.add_reaction("✅")
            database_command(f"""
              UPDATE GuildConfig 
              SET BlockedChannels = '{blocked_channels}'
              WHERE GuildID = {message.guild.id};""", ())
          else:
            await message.channel.send(dialogue(message, 'blacklist_fail'))
            await message.add_reaction("❌")
      except:
        return True
      return True
    
    case "sb!whitelist": # Whitelist current or specified channel
      try:
        message_content = message.content
        message_channel_id = message.channel.id
        blocked_channels = ast.literal_eval(database_fetch_value("BlockedChannels", "GuildConfig", f"GuildID={message.guild.id}"))
        if message_content.startswith("sb!whitelist "): 
          content = message_content.removeprefix('sb!whitelist ')
        else:
          if message_channel_id in blocked_channels:
            blocked_channels.remove(message_channel_id)
            await message.channel.send(dialogue(message, 'whitelist'))
            await message.add_reaction("✅")
            database_command(f"""
              UPDATE GuildConfig 
              SET BlockedChannels = '{blocked_channels}'
              WHERE GuildID = {message.guild.id};""", ())
          else:
            await message.channel.send(dialogue(message, 'whitelist_fail'))
            await message.add_reaction("❌")
      except:
        return True
      return True
    
    # Transformation Commands
    case "sb!transform": # Transform a user
      logger.info("Attempting to transform user...")
      args = message.content.split(' ')
      try:
        if len(message.mentions) != 1:
          raise Exception("Too many mentions")
        
        # Flags
        flags = get_flags(args)
        #forced = False
        forced = True
        if "-f" in flags:
          #if not await can_user_run_command(message):
          #  await message.channel.send(dialogue(message, 'force_transform_perms'))
          #  await message.add_reaction("❌")
          #else:
            forced = True
            flags.remove("-f")
        global_tf = False
        if "-g" in flags:
          global_tf = True
          flags.remove("-g")
        change_username = False
        if "-u" in flags:
          change_username = True
          flags.remove("-u")
        if len(flags) > 0:
          raise Exception("Invalid Flags")

        # Attachment        
        if len(message.attachments) != 1:
          raise Exception("Incorrect attachment amount")
        file = message.attachments[0]
        if not (file.filename.endswith(".tsf") or file.filename.endswith(".sbl")):
          raise Exception("Invalid File Type")
        filename = f"{ATTACHMENTS_PATH}/{file.filename}"
        await file.save(filename)
        if is_binary_file(filename):
          os.remove(filename)
          raise Exception("Binary file provided")
        try:
          if file.filename.endswith(".tsf"):
            name, avatar, text_modifiers, stutter_chance, pronouns, biography, story, fallback_prefix, fallback_suffix, fallback_muffle, fallback_alt_muffle, prefixes, suffixes, sprinkles, muffles, alt_muffles, censors, triggers, alt_triggers = decode_tsf(open(filename).read())
          
          if file.filename.endswith(".sbl"):
            name, avatar, text_modifiers, stutter_chance, pronouns, biography, story, fallback_prefix, fallback_suffix, fallback_muffle, fallback_alt_muffle, prefixes, suffixes, sprinkles, muffles, alt_muffles, censors, triggers, alt_triggers = decode_sbl(open(filename).read())
        
        except Exception as e:
          await message.add_reaction("❌")
          await message.channel.send(f'invalid schema')
          os.remove(filename)
          logger.error(e)
          logger.info("Failed to transform user")
          return True
        os.remove(filename)

        # Store transformation
        transformed = message.mentions[0]
        if transformed.id == message.author.id:
          forced = True

        if database_check_exists(("Transformations" if forced else "TransformationHolding"), f"UserID = {transformed.id} AND GuildID = {0 if global_tf else message.guild.id}"):
          database_command(f"""DELETE from {"Transformations" if forced else "TransformationHolding"} WHERE UserID={transformed.id} AND GuildID = {0 if global_tf else message.guild.id};""", ())
          database_command(f"""DELETE from "TransformationCache" WHERE UserID={transformed.id} AND GuildID = {0 if global_tf else message.guild.id};""", ())
        database_command(f"""
          INSERT INTO {"Transformations" if forced else "TransformationHolding"}
          VALUES ({transformed.id},
          {0 if global_tf else message.guild.id},
          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
          (name,
          avatar,
          text_modifiers,
          stutter_chance,
          pronouns,
          biography,
          story,
          fallback_prefix,
          fallback_suffix,
          fallback_muffle,
          fallback_alt_muffle,
          prefixes,
          suffixes,
          sprinkles,
          muffles,
          alt_muffles,
          censors,
          triggers,
          alt_triggers))
        if forced:
          if change_username:
            if global_tf:
              for guild in client.guilds:
                if transformed.id == message.guild.owner.id:
                  pass
                elif message.guild.me.top_role < transformed.top_role:
                  pass
                else:
                  await transformed.edit(nick=name)
              else:
                if transformed.id == message.guild.owner.id:
                  await message.channel.send(f'cant change owners nickname')
                elif message.guild.me.top_role < transformed.top_role:
                  await message.channel.send(f'not enough perms, please update roles to make sable top role')
                else:
                  await transformed.edit(nick=name)
          if story != None and story != "":
            await message.channel.send(story)
          else:
            await message.channel.send(dialogue(message, "transform"))
        else:
          await message.channel.send("consent")
        await message.add_reaction("✅")
        logger.info("Success")

      except Exception as e:
        await message.add_reaction("❌")
        await message.channel.send(f'<insert proper use of command>')
        logger.error(e)
        logger.info("Failed to transform user")
      
      return True
    
    case "sb!biography": # Get the biography of a transformed user
      args = message.content.split(' ')
      try:
        if len(message.mentions) != 1:
          raise Exception("Too many mentions")
        guild_tf = database_check_exists("Transformations", f"UserID = {message.mentions[0].id} AND GuildID = {message.guild.id}")
        if not database_check_exists("Transformations", f"UserID={message.mentions[0].id} AND GuildID={message.guild.id if guild_tf else 0}"):
          await message.channel.send("User isn't transformed")
          await message.add_reaction("❌")
          return True
        biography = database_fetch_value("Biography", "Transformations", f"UserID={message.mentions[0].id} AND GuildID={message.guild.id if guild_tf else 0}")
        if biography == None or biography == "":
          await message.channel.send("User doesnt have biography")
          await message.add_reaction("❌")
          return True
        await message.channel.send()
      except:
        await message.add_reaction("❌")
        await message.channel.send(f'<insert proper use of command>')
      return True
    
    case "sb!consent":
      return True
    
    case "sb!goback":
      args = message.content.split(' ')
      flags = get_flags(args)
      try:
        global_tf = False
        if "-g" in flags:
          global_tf = True
          flags.remove("-g")
        
        if len(flags) > 0:
          raise Exception("Invalid Flags")
        
        guild_id = (0 if global_tf else message.guild.id)
        if database_check_exists("Transformations", f"UserID={message.author.id} AND GuildID={guild_id}"):
          database_command(f"""INSERT INTO TransformationCache SELECT * FROM Transformations WHERE UserID=? AND GuildID=?""", (message.author.id, guild_id))
          database_command(f"""DELETE FROM Transformations WHERE UserID=? AND GuildID=?""", (message.author.id, guild_id))
        
        elif database_check_exists("TransformationCache", f"UserID={message.author.id} AND GuildID={guild_id}"):
          database_command(f"""INSERT INTO Transformations SELECT * FROM TransformationCache WHERE UserID=? AND GuildID=?""", (message.author.id, guild_id))
          database_command(f"""DELETE FROM TransformationCache WHERE UserID=? AND GuildID=?""", (message.author.id, guild_id))
        
        else:
          await message.add_reaction("❌")
          await message.channel.send(f'no transformation to go back to')
          return True
        
        await message.add_reaction("✅")

      except Exception as e:
        logger.error(e)
        await message.add_reaction("❌")
        await message.channel.send(f'<insert proper use of command>')
      return True

    # Sable Comands
    case "sb!self-destruct": # 💥
      await message.channel.send("💥")
      await message.add_reaction("💥")
      return True
    
    case "sb!hug": # Hug the girl
      await message.channel.send("hug")
      await message.add_reaction("🫂")
      return True
    
    case _:
      return False
  
  return False

# Bot Functions

@client.event
async def on_ready():
  logger.info(f'Connected as {client.user}')

@client.event
async def on_raw_reaction_add(payload):
  channel = client.get_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)
  user = client.get_user(payload.user_id)
  if message.webhook_id and str(payload.emoji) == '❓':
    try:
      author = message.guild.get_member(int(database_fetch_value("MemberID", "MessageIDs", f"ResultID={message.id}")))
      await user.send(f'This is {author.display_name} ({author.name})')
    except: return
    logger.info(f"{user.display_name} asked who {author.display_name} is")
    await message.remove_reaction(payload.emoji, user)

#@client.event
#async def on_guild_join(guild: Guild):
#  print()

@client.event
async def on_guild_remove(guild: Guild):
  if database_check_exists("GuildConfig", f"GuildID={guild.id}"):
    database_command(f"""DELETE from GuildConfig WHERE GuildID={guild.id};""", ())

@client.event
async def on_message(message: Message):
  # Early Exits
  if message.webhook_id or (message.type != MessageType.default and message.type != MessageType.reply and message.type != MessageType.chat_input_command): return
  if await fake_commands(message): return
  if not database_check_exists("GuildConfig", f"GuildID = {message.guild.id}"): return
  if len(message.stickers) != 0: return
  if message.reference is not None and message.type.value == 0: return
  if channel_blacklisted(message): return
  
	# Check if user is proxied
  if not check_is_user_is_transformed(message.guild, message.author): return

  # logger.info(f"[{message.guild.name}] ({message.author.name}) {message.content}")

  channel = message.channel
  member = message.author
  thread = MISSING
  is_in_thread = False
  if isinstance(channel, Thread):
    thread = channel
    channel = channel.parent
    is_in_thread = True

  # Get or create webhook
  webhooks = await channel.webhooks()
  webhookActive = False
  for hook in webhooks:	
    if hook.name == 'bodyProxy': 
      webhookActive = True
      webhook = hook
  if not webhookActive: 
    webhook = await channel.create_webhook(name='bodyProxy')
  
  # Setup message
  guild_tf = database_check_exists("Transformations", f"UserID = {message.author.id} AND GuildID = {message.guild.id}")

  if message.content != "":
    try:
      content = apply_speech(message.content, message.author.id, message.guild.id if guild_tf else 0)
    except Exception as e:
      logger.error(e)
      logger.info(f"[{message.guild.name}] ({message.author.name}) {message.content if message.content != "" else "Message was empty"}")
  else:
    content = ""
  files = []
  filesLinks = []
  for attachment in message.attachments:
    filesLinks.append(attachment.url)
    file = await attachment.to_file(spoiler=attachment.is_spoiler())
    files.append(file)
  embeds: List[Embed] = []
  if message.reference:
    if REPLY_TYPE == "EMBED":
      embeds.insert(0, reply_embed(message))
    elif REPLY_TYPE == "TRANSFORMATE":
      content = reply_transformate(message) + content
  
	# Webhook
  has_server_tf = database_check_exists("Transformations", f"UserID={member.id} AND GuildID={message.guild.id}")
  username = database_fetch_value("Name", "Transformations", f"UserID={member.id} AND GuildID={message.guild.id if has_server_tf else 0}", )
  avatar_url = database_fetch_value("Avatar", "Transformations", f"UserID={member.id} AND GuildID={message.guild.id if has_server_tf else 0}")
  result = await webhook.send(
    content = content,
    files = files,
    embeds = embeds,
    avatar_url = avatar_url,
    username = username,
    thread = thread,
    wait = True
  )
  
  database_command(f"""
    INSERT INTO MessageIDs
    VALUES ({result.id}, {member.id}, {channel.id}, {thread.id if is_in_thread else 0});""", ())
  await message.delete()

@client.event
async def close():
  logger.info("Disconnected")
  database_connection.close()
  #await client.get_guild(1320173671817412678).get_channel(1375603415237001226).send("<@473309618081234945> I'm being turned off, is that intentional?")

client.run(TOKEN, root_logger=True)