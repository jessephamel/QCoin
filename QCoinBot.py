import discord
import asyncio
from tinydb import TinyDB, Query
from discord.ext import commands
from dotenv import dotenv_values
import json

# get env variables
config = dotenv_values("tokens.env")

# initalize
intents = discord.Intents(messages=True, guilds=True, members=True)

client = discord.Client()
bot = commands.Bot(command_prefix='!', intents=intents)

db = TinyDB('qcoin_db.json')
store_db = TinyDB('store_db.json')

# print to console when logged in to discord
@bot.event
async def on_ready():
    print('We have logged in')

# ///////////////////////////////////////////////////////// Helper Functions

# check if the command was run by me
def is_me(ctx):
    return ctx.message.author.id == int(config['MY_USER_ID'])

# return the stock of specified item
def getItemStock(user_id, item):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['inventory']

    return u[item]

# return the coin balance of specified user
def getCoinsBalance(user_id):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['coins']

    return u

# return the coin balance of specified user
def setCoinsBalance(user_id, balance):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['coins']

    db.update({'coins': balance}, q.user_id == user_id)

# return the inventory of specified user
def getUserInventory(user_id):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['inventory']

    return u

# ///////////////////////////////////////////////////////// Admin Bot Commands

# insert the users that don't already exist
@bot.command(name='initdb')
@commands.check(is_me)
async def initdb(ctx):
    global db

    g = ctx.message.guild
    a = ctx.message.author

    g_members = await g.chunk()
    q = Query()

    for m in g_members:
        if len(db.search(q.user_id == int(m.id))) == 0:
            db.insert({'user_id': m.id, 
                        'name': m.name,
                        'coins': 100,
                        'inventory': {'bread': 1, 'games': 1}
                        })
            print('inserting {}'.format(m.id))

# mint coins for me only
@bot.command(name='mint')
@commands.check(is_me)
async def mint(ctx, amount):
    global db

    g = ctx.message.guild
    a = ctx.message.author

    a_bal = getCoinsBalance(config['MY_USER_ID'])

    setCoinsBalance(config['MY_USER_ID'], a_bal+int(amount))

# ///////////////////////////////////////////////////////// User Bot Commands

# give coins to a user
@bot.command(name='give')
async def give(ctx, arg1, amount=0):
    global db

    g = ctx.message.guild
    a = ctx.message.author
    r = ctx.message.mentions[0]
    q = Query()

    if a.id != r.id:
        try:
            a_bal = getCoinsBalance(int(a.id))
            r_bal = getCoinsBalance(int(r.id))
            if int(amount) > 0:
                if a_bal > int(amount):
                    r_bal += amount
                    a_bal -= amount
                    setCoinsBalance(int(r.id), r_bal)
                    setCoinsBalance(int(a.id), a_bal)
                    await ctx.send(f"**{amount}** coins given to {r.name}")
                else:
                    await ctx.send("Insufficient funds!")
        except:
            await ctx.send("Invalid amount")

# get your coin balance
@bot.command(name='balance')
async def balance(ctx):
    global db

    g = ctx.message.guild
    a = ctx.message.author

    q = Query()

    b = getCoinsBalance(a.id)
    b_string = f"**{a.name}**, your QuadeCoin balance is: **{b}**"
    await ctx.send(b_string)    

# get the inventory of your own or another user
@bot.command(name='inventory')
async def inventory(ctx):
    global db

    g = ctx.message.guild
    a = ctx.message.author

    q = Query()

    # recipient = db.search(q.user_id == int(r.id))[0]
    u_inv = getUserInventory(a.id)
    inv_string = f"**{a.name}** has the following in their inventory:\n"
    for i in u_inv:
        for k in i.keys():
            inv_string += f"**{i[k]}** {k}\n"
    await ctx.send(inv_string)

bot.run(config['MY_TOKEN'])