import discord
import random

client = discord.Client()

class counter():
    interval = random.randrange(7, 15)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    client.change_presence(game=discord.Game(name='in the 8 Isles!'))
    #print('starting rp...')
    #threading.Thread(target=roleplay, args=(client,)).start()
    print('------')

@client.event
async def on_message(message):
    print(counter.interval)
    counter.interval -= 1
    if counter.interval < 1:
        await client.send_message(message.channel, '*squeak*')
        counter.interval = random.randrange(7, 15)

client.run('NDczNjgyMjAxNzU4NjYyNjU2.DkFfEA.AvF5ZsYmSq53Y20hwKH_fLJ0Ork')
