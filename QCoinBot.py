import discord
import asyncio
from tinydb import TinyDB, Query
from discord.ext import commands
from dotenv import dotenv_values
from urllib.request import urlopen
from datetime import datetime, timedelta, timezone
import json

# get env variables
config = dotenv_values("tokens.env")

# initalize
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents)

db = TinyDB('qcoin_db.json')
qdb = db.table('users', cache_size=0)

# print to console when logged in to discord
@bot.event
async def on_ready():
    print('We have logged in')

# ///////////////////////////////////////////////////////// Helper Functions

def getCurrentTime():
    res = urlopen('http://worldtimeapi.org/api/timezone/America/Vancouver')
    result = res.read().strip()
    result_str = result.decode('utf-8')
    result_json = json.loads(result_str)
    datetime_str = result_json['datetime']

    return datetime_str

def addUser(user_id):
    global qdb

    q = Query()

    ct = getCurrentTime()

    if len(qdb.search(q.user_id == int(user_id))) == 0:
        qdb.insert({'user_id': int(user_id), 
                    'coins': 100,
                    'tickets': 0,
                    'lastDaily': ct
                    })
        print('inserting {}'.format(user_id))

# check if the command was run by me
def is_me(ctx):
    return ctx.message.author.id == int(config['MY_USER_ID'])

# return the coin balance of specified user
def getCoinsBalance(user_id):
    global qdb

    q = Query()

    if len(qdb.search(q.user_id == int(user_id))) == 0:
        addUser(user_id)

    u = qdb.search(q.user_id == int(user_id))[0]['coins']
    return u

# return the coin balance of specified user
def setCoinsBalance(user_id, balance):
    global qdb

    q = Query()

    if len(qdb.search(q.user_id == int(user_id))) == 0:
        addUser(user_id)

    qdb.update({'coins': balance}, q.user_id == user_id)

# return the last daily usage
def getLastDaily(user_id):
    global qdb

    q = Query()

    if len(qdb.search(q.user_id == int(user_id))) == 0:
        addUser(user_id)

    u = qdb.search(q.user_id == int(user_id))[0]['lastDaily']

    return u

# set the last daily usage
def setLastDaily(user_id, dt):
    global qdb

    q = Query()

    if len(qdb.search(q.user_id == int(user_id))) == 0:
        addUser(user_id)

    qdb.update({'lastDaily': dt}, q.user_id == user_id)

# ///////////////////////////////////////////////////////// Admin Bot Commands

# insert the users that don't already exist
@bot.command(name='initdb')
@commands.check(is_me)
async def initdb(ctx):
    global qdb

    g = ctx.message.guild
    a = ctx.message.author

    g_members = await g.chunk()
    q = Query()

    ct = getCurrentTime()
    
    for m in g_members:
        if len(qdb.search(q.user_id == int(m.id))) == 0:
            qdb.insert({'user_id': int(m.id), 
                        'coins': 100,
                        'tickets': 0,
                        'lastDaily': ct
                        })
            print('inserting {}'.format(m.id))

# mint coins for me only
@bot.command(name='mint')
@commands.check(is_me)
async def mint(ctx, amount):
    g = ctx.message.guild
    a = ctx.message.author

    a_bal = getCoinsBalance(int(config['MY_USER_ID']))

    setCoinsBalance(int(config['MY_USER_ID']), a_bal+int(amount))

# ///////////////////////////////////////////////////////// User Bot Commands

# give coins to a user
@bot.command(name='give')
async def give(ctx, arg1, amount=0):
    g = ctx.message.guild
    a = ctx.message.author
    r = ctx.message.mentions[0]

    if a.id != r.id:
        try:
            a_bal = getCoinsBalance(int(a.id))
            r_bal = getCoinsBalance(int(r.id))
            if int(amount) > 0:
                if a_bal >= int(amount):
                    r_bal += amount
                    a_bal -= amount
                    setCoinsBalance(int(r.id), r_bal)
                    setCoinsBalance(int(a.id), a_bal)
                    await ctx.reply(f"ℚ**{amount}** given to <@{r.id}>. Your new balance is ℚ**{a_bal}**")
                else:
                    await ctx.reply("Insufficient funds!")
            else:
                await ctx.reply("Invalid amount")
        except:
            await ctx.reply("Invalid amount")

# get your coin balance
@bot.command(name='balance')
async def balance(ctx):
    g = ctx.message.guild
    a = ctx.message.author

    b = getCoinsBalance(a.id)
    b_string = f"<@{a.id}>, your QuadeCoin balance is: ℚ**{b}**"
    await ctx.reply(b_string)

# get the mudae role
@bot.command(name='mud')
async def mud(ctx):
    g = ctx.message.guild
    a = ctx.message.author

    mud_role = discord.utils.get(ctx.guild.roles, name="Test")
    mud_channel = discord.utils.get(ctx.guild.text_channels, name="test")
    member = g.get_member(a.id)

    m_bal = getCoinsBalance(a.id)
    if m_bal > 25:
        newBal = m_bal - 25
        setCoinsBalance(int(a.id), newBal)

        await member.add_roles(mud_role)
        await ctx.send(f"{a.name}, you have access to <#1187511999404462221> for 60 seconds!")
        print(mud_channel)
        await asyncio.sleep(60)
        await member.remove_roles(mud_role)
    else:
        await ctx.send("Insufficient funds!")

@bot.command(name='daily')
async def daily(ctx):
    g = ctx.message.guild
    a = ctx.message.author

    ct = getCurrentTime()
    current_daytime = datetime.strptime(ct, '%Y-%m-%dT%H:%M:%S.%f%z')
    current_day = current_daytime.replace(hour=0, minute=0, second=0)
    last_daily = datetime.strptime(getLastDaily(a.id), '%Y-%m-%dT%H:%M:%S.%f%z').replace(hour=0, minute=0, second=0)
    next_day = (current_day + timedelta(days=1, hours=0, minutes=0, seconds=0)) - current_daytime
    next_day = datetime.strptime(str(next_day), '%H:%M:%S')
    td = current_day - last_daily

    print(td.days)
    if td.days >= 1:
        current_bal = int(getCoinsBalance(a.id))
        newBal = current_bal + 100
        setCoinsBalance(a.id, newBal)
        setLastDaily(a.id, ct)
        await ctx.send(f'Daily claimed! Your new balance is ℚ{newBal}')
    else:
        await ctx.send(f'Already claimed daily! Next daily in {next_day.hour} hours, {next_day.minute} minutes, {next_day.second} seconds')

bot.run(config['MY_TOKEN'])