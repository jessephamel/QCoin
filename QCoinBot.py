import discord
import asyncio
from tinydb import TinyDB, Query
from discord.ext import commands
import os
import json

# initalize
intents = discord.Intents(messages=True, guilds=True, members=True)

client = discord.Client()
bot = commands.Bot(command_prefix='!', intents=intents)

db = TinyDB('qcoin_db.json')

# check if the command was run by me
def is_me(ctx):
    return ctx.message.author.id == MY_USER_ID

# return the stock of specified item
def getItemStock(user_id, item):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['inventory']

    return u[item]

# return the inventory of specified user
def getUserInventory(user_id):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]['inventory']

    return u

# set the stock of specified user's item
def setItemStock(user_id, item, amount):
    global db

    q = Query()
    u = db.search(q.user_id == int(user_id))[0]

    for i in 
    u['inventory']:
        if i['name'].upper() == item.upper():
            i['amount'] = int(amount)
    # db.upsert(u, (q.user_id == int(user_id)))

# print to console when logged in to discord
@bot.event
async def on_ready():
    print('We have logged in')

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
                        'inventory': [] 
                        })
            print('inserting {}'.format(m.id))
        else:
            print('already exists')

# add an item to the db
@bot.command(name='additem')
@commands.check(is_me)
async def additem(ctx, arg1):
    add_Item(arg1)

# set the stock of item in db
@bot.command(name='setamt')
@commands.check(is_me)
async def setamt(ctx, arg1, item, amount):
    global db

    r = ctx.message.mentions[0]

    print(item)
    print(amount)

    setItemStock(int(r.id), item, amount)

# give coins or an item to a user
@bot.command(name='give')
async def give(ctx, arg1, amount=0, item='QC'):
    global db

    g = ctx.message.guild
    a = ctx.message.author
    r = ctx.message.mentions[0]
    q = Query()

    item = item.upper()

    if a.id != r.id:
        try:
            a_stock = getItemStock(int(a.id), item)
            r_stock = getItemStock(int(r.id), item)
            if int(amount) > 0:
                if a_stock > int(amount):
                    r_stock += amount
                    a_stock -= amount
                    setItemStock(int(r.id), item, r_stock)
                    setItemStock(int(a.id), item, a_stock)
                    await ctx.send("{0} {1} given to {2}".format(amount, item, r.name))
                else:
                    await ctx.send("Insufficient funds!")
        except KeyError:
            await ctx.send("Item {} not found!".format(item))

# get the inventory of your own or another user
@bot.command(name='inventory')
async def inventory(ctx):
    global db

    g = ctx.message.guild
    a = ctx.message.author
    r = ctx.message.mentions
    q = Query()

    # recipient = db.search(q.user_id == int(r.id))[0]
    if len(r) == 0:
        u_inv = getUserInventory(a.id)
        inv_string = "**{0}** has the following in their inventory:\n".format(a.name)
        for k in u_inv.keys():
            inv_string += "**{}** {}\n".format(u_inv[k], k)
        await ctx.send(inv_string)
    elif len(r) == 1:
        u_inv = getUserInventory(r[0].id)
        inv_string = "**{0}** has the following in their inventory:\n".format(r[0].name)
        for k in u_inv.keys():
            inv_string += "**{}** {}\n".format(u_inv[k], k)
        await ctx.send(inv_string)

bot.run(TOKEN)