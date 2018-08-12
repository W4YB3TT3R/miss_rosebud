import discord
import requests
import wishify
import errno
import os
import pickle
import random
import traceback
import sys, re
import rosebud_configs
import asyncio
import chat

from profiles import Profile, Stickers,  TooSoonError
from datetime import datetime, timedelta
from bidict import marriage
from collections.abc import MutableMapping
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from io import BytesIO
from PIL import Image

trans = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
client = discord.Client()
prefix = ',,'
moneyrange = (10, 15)

#current main settings in case I change config categories later
settings = rosebud_configs.settings

elid = '181057933654622208'
wishid = '304080356900995092'
roseid = '464161516212715530'

kicked = []

#marriage commands
commands = {
            'marry':            'usage: {}marry [@user]'.format(prefix),
            'acceptmarriage':   'usage: {}acceptmarriage [@user]'.format(prefix),
            'denymarriage':     'usage: {}denymarriage [@user]'.format(prefix),
            'divorce':          'usage: {}divorce'.format(prefix)
            }
#misc commands
misccommands = {
                'wishify':          'usage: {}wishify {{url}} {{color hex}}'.format(prefix),
                'dlprofile':        'usage: {}dlprofile {{@user}}'.format(prefix),
                'dlemoji':          'usage: {}dlprofile [emoji]'.format(prefix),
                'profile':          'usage: {}profile {{@user}}'.format(prefix),
                'gay':              'usage: {}gay {{@user|url}}'.format(prefix),
                'hotel':            'usage: {}hotel {{@user|url}}'.format(prefix),
                'daily':            'usage: {}daily'.format(prefix),
                'shakeyshakey':     'usage: {}shakeyshakey {{cat1|cat2|spinda|tortgle}}'.format(prefix),
                'pay':     'usage: {}pay [@user] [amount]'.format(prefix),
                'bal':     'usage: {}bal'.format(prefix),
                'invite':     'usage: {}invite'.format(prefix)
            }
#admin commands
admincommands = {
            'kick':             'usage: {}kick {{@user}} [@user...]'.format(prefix)
            }

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name.translate(trans))
    print(client.user.id)
    client.change_presence(game=discord.Game(name='in the 8 Isles!'))
    #print('starting rp...')
    #threading.Thread(target=roleplay, args=(client,)).start()
    print('------')

def safety(func):
    async def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print('Uncaught exception {}, ignoring...'.format(repr(e)))
    return decorator

@client.event
async def on_member_remove(member):
    farewell = 'Cya {} lmao.'
    if member.server.id == rosebud_configs.settings.setting['main_server_id']:
        if member in kicked:
            kicked.remove(member)
            farewell = '{} bye bitch.'
        await client.send_message(client.get_channel(rosebud_configs.settings.setting['entry_channel_id']), farewell.format(member.mention))

@safety
@client.event
async def on_message(message):

    if message.channel.is_private and message.author.id == wishid:
        links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        e = discord.Embed(title=message.author.name.translate(trans), description=message.content)
        if len(message.attachments)>0:
            e.set_image(url=message.attachments[0]['url'])
        elif len(links)>0:
            e.set_image(url=links[0])
        await client.send_message(discord.utils.get(client.get_all_channels(), id='475034267928363019'), embed=e)
        print('{} to wishi: {}'.format(message.author.name.translate(trans), message.content.translate(trans)))

    elif message.content.startswith('{}tellwishi'.format(prefix)) and not wishid in [i.id for i in message.server.members]:
        links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        e = discord.Embed(title=message.author.name.translate(trans), description=message.content.strip('{}tellwishi'.format(prefix)))
        if len(message.attachments)>0:
            e.set_image(url=message.attachments[0]['url'])
        elif len(links)>0:
            e.set_image(url=links[0])
        await client.send_message(await client.get_user_info(wishid), embed=e)
        print('{} to wishi: {}'.format(message.author.name.translate(trans), message.content.translate(trans).strip('{}tellwishi'.format(prefix))))
    
    elif ('WHO\'S YOUR DADDY' in message.content.upper() or 'WHO\'S YOUR BIG DADDY' in message.content.upper()) and message.author.id == wishid:
        await client.send_message(message.channel, "Hoshi!")
        
    elif message.content.startswith('{}help'.format(prefix)):
        try:
            await client.send_message(message.channel, {**commands, **misccommands, **admincommands}[message.content.split(' ')[1]])
        except:
            send = discord.Embed(title='٩( ᐛ )و  Commands!', color=0xffd1dc)
            send.set_author(name='Miss Rosebud', icon_url=client.user.avatar_url)
            send.add_field(name='✿ marriage commands ✿',value='```{}```'.format(re.sub('[\[\]\']', '', str(list(commands.keys())))), inline=False)
            send.add_field(name='✿ miscellaneous ✿', value='```{}```'.format(re.sub('[\[\]\']', '', str(list(misccommands.keys())))), inline=False)
            #send = '٩( ᐛ )و  Commands!\n✿ marriage commands ✿\n{}\n\n✿ miscellaneous ✿\n{}\n\nMore to come. ;3c'.format(
            #    re.sub('[\[\]\']', '', str(list(commands.keys()))), re.sub('[\[\]\']', '', str(list(misccommands.keys()))))
            await client.send_message(message.channel, embed=send)

    elif message.content.startswith('{}wishify'.format(prefix)):
        try:
            print(message.author.id)
            arg = message.content.strip().split(' ')
            color = 'ffd1dc'
            imurl = ''
            
            if len(message.attachments)>0:
                imurl = message.attachments[0]['url']
                try:
                    color = arg[1].strip('#')
                except:
                    color = 'ffd1dc'
                print(imurl)
            elif len(arg)>1:
                imurl = arg[1]
                try:
                    color = arg[2]
                except:
                    color = 'ffd1dc'
                print(imurl)
            else:
                await client.send_message(message.channel, 'please specify an image to wishify! xwu\"')
                return

            #open and convert to PNG
            response = requests.get(imurl)
            top = Image.open(BytesIO(response.content))
            im = Image.new('RGBA', top.size)
            im.paste(top, (0,0))

            #im = Image.open(BytesIO(response.content))
            colored = ''
            try:
                colored = wishify.colorify(im, color)
            except MemoryError:
                await client.send_message(message.channel, 'It\'s too big for me! \_(´ཀ`」 ∠)')
            except Exception as e:
                print('colorify exception: {}'.format(repr(e)))
            
            #colored.show()

            await send_image(colored, client, message.channel)
            
            '''
            try:
                colored.save('temp.png')
                await client.send_file(message.channel, 'temp.png')
            except Exception as e:
                print('exception in temp block!')
                print('error: {}'.format(str(e)))
            finally:
                await silentremove('temp.png')
            '''
            
        except Exception as e:
            print(e)
            await client.send_message(message.channel, misccommands['wishify'])
        
        #await client.send_message(message.channel, message.embeds[0].image.url)

    elif message.content.startswith('{}updatestatus'.format(prefix)) and message.author.id in (elid, wishid):
        await client.change_presence(game=discord.Game(name=message.content.split(' ',1)[1]))

    

    elif message.content.startswith('{}marry'.format(prefix)):
        try:
            target = message.mentions[0]
            
            if target.id == message.author.id:
                await client.send_message(message.channel, 'Marrying yourself? This is so sad, Music Baby play despacito')
                return
            if target.id == '464161516212715530':
                await client.send_message(message.channel, 'My robot heart belongs to Queen Wishi. xwu')
                return
            
            for i in readmarriages():
                if target.id in i:
                    raise ThemMarriedError('them already married', None)
                if message.author.id in i:
                    raise YouMarriedError('you already married', None)
            propose(message.author.id, target.id)
            print('{} proposed to {}'.format(message.author.name.translate(trans), target.name.translate(trans)))
            await client.send_message(message.channel, '<@{}>, will you accept <@{}>\'s proposal? Use {}acceptmarriage [user] or {}denymarriage [user].'.format(target.id, message.author.id, prefix, prefix))
            
        except ThemMarriedError:
            await client.send_message(message.channel, 'The person you\'re trying to marry is already taken, bucko. ;3€')
        except YouMarriedError:
            await client.send_message(message.channel, 'YOU\'RE ALREADY MARRIED CUCK {}'.format(gibberish().upper()))
        except:
            traceback.print_exc()
            await client.send_message(message.channel, commands['marry'])
        
    elif message.content.startswith('{}acceptmarriage'.format(prefix)):
        try:
            target = message.mentions[0]
            for i in readmarriages():
                if message.author.id in i:
                    raise YouMarriedError('you already married', None)
                if target.id in i:
                    raise ThemMarriedError('them already married', None)
            if readproposals()[target.id] == message.author.id:
                print('marrying...')
                acceptmarriage(message.author.id, target.id)
                await client.send_message(message.channel, 'Congratulations on your marriage!! xvo')
                print('married {} to {}'.format(message.author.name.translate(trans), target.name.translate(trans)))
                await Stickers.award(target.id, 'Married')
                await Stickers.award(message.author.id, 'Married')
                return
            await client.send_message(message.channel, 'You haven\'t been proposed to by them idiot {}'.format(gibberish()))
        except KeyError:
            await client.send_message(message.channel, 'They haven\'t proposed to anyone... yet. xwo'.format(gibberish()))
        except ThemMarriedError:
            await client.send_message(message.channel, 'The person you\'re trying to marry is already taken, bucko. ;3€')
        except YouMarriedError:
            await client.send_message(message.channel, 'YOU\'RE ALREADY MARRIED CUCK {}'.format(gibberish().upper()))
        except IndexError:
            await client.send_message(message.channel, 'Please specify someone who\'s proposed to you xvo')
        except:
            traceback.print_exc()
            await client.send_message(message.channel, commands['acceptmarriage'])

    elif message.content.startswith('{}denymarriage'.format(prefix)):
        try:
            target = message.mentions[0]
            if readproposals()[target.id] == message.author.id:
                await client.send_message(message.channel, 'Get cucked {}'.format(target.name.translate(trans)))
                print('{} denied {}'.format(message.author.name.translate(trans), target.name.translate(trans)))
                return
            await client.send_message(message.channel, 'Pff, you wish they\'d propose to you, cuck.')
        except KeyError:
            await client.send_message(message.channel, '{} doesn\'t have any proposals right now.'.format(target.name.translate(trans)))
        except:
            traceback.print_exc()
            await client.send_message(message.channel, commands['denymarriage'])

    elif message.content.startswith('{}divorce'.format(prefix)):
        try:
            for i in readmarriages():
                if message.author.id in i:
                    print(message.author.id)
                    print(i)
                    await client.send_message(message.channel, 'Damn, relationship ended with <@{}>. :pensive: That\'s so sad, can we get 50 likes? At least you have your Queen Wishi as a spouse, probably. If you deserve it. ;3€'.format(readmarriages()[message.author.id]))
                    delmarriage(message.author.id)
                    print('{} was divorced'.format(message.author.name.translate(trans)))
                    await Stickers.award(message.author.id, 'Divorced')
                    return
            await client.send_message(message.channel, 'As if anyone cared enough to get married to you in the first place.')
        except:
            traceback.print_exc()
            await client.send_message(message.channel, commands['divorce'])

    elif message.content.startswith('{}wishimarry'.format(prefix)) and (message.author.id == wishid):
        try:
            target = message.mentions[0]
            wishimarriages = readwmarriages()
            writewmarriage(target.id)
            if target.id in wishimarriages:
                delta = datetime.now()-wishimarriages[target.id]['anniversary']
                if target.id == roseid:
                    await client.send_message(message.channel, 'K-kya!! ( ˘͈ ᵕ ˘͈♡) Well my Queen,, if you insist. I love you so much!! >w<` I\'m so embarrassed and happy aah,,')
                    return
                await client.send_message(message.channel, 'Congratulations on marriage #{} in the {} since {} xwu'.format(
                    wishimarriages[target.id]['marriages']+1,
                    "{} day(s) and {} seconds".format(delta.days, delta.seconds),
                    wishimarriages[target.id]['anniversary'].strftime("%Y-%m-%d")
                    ))
            else:
                if target.id == roseid:
                    await client.send_message(message.channel, 'K-kya!! ( ˘͈ ᵕ ˘͈♡) Well my Queen,, if you insist. I love you so much!! >w<` I\'m so embarrassed and happy aah,,')
                else:
                    await client.send_message(message.channel, 'Congratulations on your first marriage with Queen Wishi, <@{}>!'.format(target.id))
            await Stickers.award(target.id, 'WishiMarried')
        except:
            traceback.print_exc()

    elif message.content.startswith('{}wishidivorce'.format(prefix)) and (message.author.id == wishid):
        try:
            target = message.mentions[0]
            delwmarriage(target.id)
            await client.send_message(message.channel, 'Cya thottie ;3c')
            await Stickers.unaward(target.id, 'WishiMarried')
        except KeyError:
            await client.send_message(message.channel, 'You\'re not married to them yet, my Queen.')
        except IndexError:
            await client.send_message(message.channel, 'Please specify a thot to destroy, my Queen!')
        except:
            traceback.print_exc()
        
    elif message.content.startswith('{}makepickles'.format(prefix)) and message.author.id == elid:
        await client.send_message(message.channel, 'Pickles created!')
        with open('{}/directory.pk'.format(settings.home_dir), 'wb+') as f:
            marriages = marriage()
            marriages['lucky'] = 'dante'
            pickle.dump(marriages, f)
        with open('{}/proposals.pk'.format(settings.home_dir), 'wb+') as f:
            proposals = {'lucky':'dante'}
            pickle.dump(proposals, f)

    elif message.content.startswith('{}makewmar'.format(prefix)) and message.author.id == elid:
        await client.send_message(message.channel, 'Wishi flavored pickles created!')
        with open('{}/wishidirectory.pk'.format(settings.home_dir), 'wb+') as f:
            marriages = dict()
            marriages['lucky'] = 'dante'
            pickle.dump(marriages, f)

    elif message.content.startswith('{}makeprofiles'.format(prefix)) and message.author.id == elid:
        with open('{}/userlist.pk'.format(settings.home_dir), 'wb+') as f:
            profiles = dict()
            #profiles['lucky'] = 'dante'
            pickle.dump(profiles, f)
        
        await client.send_message(message.channel, 'profiles created!')

    elif message.content.startswith('{}dlemoji'.format(prefix)):
        try:
            response = requests.get(discord.utils.get(client.get_all_emojis(), name = message.content.split(':')[1]).url)
            await send_image(Image.open(BytesIO(response.content)), client, message.channel)
        except:
            await client.send_message(message.channel, commands['dlemoji'])

    elif message.content.startswith('{}dlprofile'.format(prefix)):
        if len(message.mentions) > 0:
            target = message.mentions[0]
        else:
            target = message.author
        
        response = requests.get(target.avatar_url if message.author.avatar_url != '' else target.default_avatar_url)
        profile = Image.open(BytesIO(response.content))

        await send_image(profile, client, message.channel)

    #elif message.content.startswith('{}wtrain'.format(prefix)):
    #    print('aaaaaaa')
    #    await client.send_message(message.channel, 'Training...')
    #    chat.holder(message.channel, client)
    #    await client.send_message(message.channel, 'Training complete')

    elif message.content.startswith('{}gay'.format(prefix)):
        if len(message.mentions) > 0:
            target = message.mentions[0]
        else:
            target = message.author

        try:
            if len(message.attachments)>0:
                imurl = message.attachments[0]['url']
            else:
                imurl = message.content.split()[1]
            response = requests.get(imurl)
        except:
            response = requests.get(target.avatar_url if message.author.avatar_url != '' else target.default_avatar_url)
            
        profile = Image.open(BytesIO(response.content))

        overlay = Image.open('{}/pretty.png'.format(settings.home_dir))
        if profile.size[0] > overlay.size[0]:
            profile.thumbnail(overlay.size, Image.ANTIALIAS)
        else:
            premultiply(overlay)
            overlay.thumbnail(profile.size, Image.ANTIALIAS)
            unmultiply(overlay)
        profile.paste(overlay, (0,0), overlay)
        
        await send_image(profile, client, message.channel)

    elif message.content.startswith('{}nikki'.format(prefix)):
        if len(message.mentions) > 0:
            target = message.mentions[0]
        else:
            target = message.author

        try:
            if len(message.attachments)>0:
                imurl = message.attachments[0]['url']
            else:
                imurl = message.content.split()[1]
            response = requests.get(imurl)
        except:
            response = requests.get(target.avatar_url if message.author.avatar_url != '' else target.default_avatar_url)

        profile = Image.open(BytesIO(response.content))
        overlay = Image.open('{}/nikki.png'.format(settings.home_dir))
        canvas = Image.new('RGB', overlay.size, (255, 255, 255))

        
        if profile.size[1] > 200:
            profile.thumbnail((1000, 200), Image.ANTIALIAS)
        else:
            profile = profile.resize((200, profile.size[0]//profile.size[1]*200), Image.BICUBIC)
        
        canvas.paste(profile, (0,200))
        canvas.paste(overlay, (0,0), overlay)
        
        await send_image(canvas, client, message.channel)

    elif message.content.startswith('{}hotel'.format(prefix)):
        if len(message.mentions) > 0:
            target = message.mentions[0]
        else:
            target = message.author

        try:
            if len(message.attachments)>0:
                imurl = message.attachments[0]['url']
            else:
                imurl = message.content.split()[1]
            response = requests.get(imurl)
        except:
            response = requests.get(target.avatar_url if message.author.avatar_url != '' else target.default_avatar_url)
            
        profile = Image.open(BytesIO(response.content))

        overlay = Image.open('{}/mario.png'.format(settings.home_dir))
        if profile.size[0] > overlay.size[0]:
            profile.thumbnail(overlay.size, Image.ANTIALIAS)
        else:
            premultiply(overlay)
            overlay.thumbnail(profile.size, Image.ANTIALIAS)
            unmultiply(overlay)
        profile.paste(overlay, (0,profile.size[1]-overlay.size[1]), overlay)
        
        await send_image(profile, client, message.channel)

    elif message.content.startswith('{}shakeyshakey'.format(prefix)):
        dances = {
                'cat1': 'https://cdn.discordapp.com/attachments/425046327047487500/474442976802897940/image.gif',
                'cat2': 'https://cdn.discordapp.com/attachments/425046327047487500/474443228364537856/fuck_this_pussy_boy.gif',
                'spinda': 'https://play.pokemonshowdown.com/sprites/xyani/spinda.gif',
                'tortgle': 'https://cdn.discordapp.com/attachments/425057165959495690/472646921060876288/received_967505780079985.gif'
                }
        try:
            dance = dances[message.content.split()[1]]
        except:
            dance = random.choice(list(dances.values()))

        e = discord.Embed()
        e.set_image(url=dance)
        await client.send_message(message.channel, embed=e)
    
    elif message.content.startswith('{}profile'.format(prefix)):
        try:
            if len(message.mentions) > 0:
                target = message.mentions[0]
            else:
                target = message.author

            await client.send_message(message.channel, embed=await Profile(target).get_card_plaintext(client))
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            await client.send_message(message.channel, misccommands['profile'])

    elif message.content.startswith('{}daily'.format(prefix)):
        target = Profile(message.author)
        try:
            if message.author.id == wishid:
                await client.send_message(message.channel, 'Added {} {} to your account, my Queen. Feel free to ask for more. xwu'.format(await target.daily(), Profile.currency_name))
                return
            await client.send_message(message.channel, 'Added {} {} to your account for today!'.format(await target.daily(), Profile.currency_name))
        except TooSoonError as e:
            await client.send_message(message.channel, 'Please wait {:.2f} hours before begging for more {}.'.format(e.waittime.seconds / 3600.0, Profile.currency_name))
        except Exception as e:
            print(repr(e))
            await client.send_message(message.channel, misccommands['daily'])

    elif message.content.startswith('{}pay'.format(prefix)):
        try:
            payer = Profile(message.author)
            recipient = Profile(message.mentions[0])
            amount = int(message.content.split()[2])
            if payer.id == wishid:
                recipient.amend_currency(amount)
                await client.send_message(message.channel, 'Queen Wishi has amended {}\'s balance by {}{}.'.format(message.author.mention, message.mentions[0].mention, Profile.currency_symbol, amount))
            elif amount <= 0:
                await client.send_message(message.channel, 'You can\'t pay {} idiot {}.'.format(amount, gibberish()))
                return
            elif payer.id == recipient.id:
                await client.send_message(message.channel, 'Trying to defraud me? Nice try idiot.')
                return
            elif message.mentions[0].bot:
                await client.send_message(message.channel, 'You can\'t even buy a bot\'s love, small dick energy cuck.')
                return
            elif payer.get_balance() >= amount:
                payer.amend_currency(-amount)
                recipient.amend_currency(amount)
                await client.send_message(message.channel, '{} has paid {} {}{}'.format(message.author.mention, message.mentions[0].mention, Profile.currency_symbol, amount))
            else:
                await client.send_message(message.channel, 'Insufficient funds, ya broke cuck.')
        except:
            await client.send_message(message.channel, misccommands['pay'])

    elif message.content.startswith('{}bal'.format(prefix)):
        e = discord.Embed(title='{}\'s balance'.format(message.author.name.translate(trans)), description='{}{}'.format(Profile.currency_symbol, Profile(message.author).get_balance()))
        await client.send_message(message.channel, embed=e)
        
    elif message.content.startswith('{}invite'.format(prefix)):
        await client.send_message(message.channel, 'https://discordapp.com/oauth2/authorize?client_id=464161516212715530&scope=bot')

    elif message.content.startswith('{}kick'.format(prefix)):
        try:
            assert message.channel.permissions_for(message.author).administrator
            for i in message.mentions:
                await client.kick(i)
                kicked.append(i)
            await client.send_message(message.channel, 'Butts kicked.')
        except AssertionError:
            await client.send_message(message.channel, 'Command only authorized for admins against people with roles lower than mine! smh cmh')
        except discord.Forbidden:
            await client.send_message(message.channel, 'You haven\'t given me that power. Command only authorized for admins against people with roles lower than mine. ( xmu)')
        except Exception as e:
            print(repr(e))
            print(e)
            await client.send_message(message.channel, admincommands['kick'])
    
    elif message.content.startswith('{}baka'.format(prefix)) or message.content.startswith('{}bitch'.format(prefix)):
        with open('watashipasta.txt', 'r') as f:
            await client.send_message(message.channel, f.read())

    elif message.content.startswith('{}test'.format(prefix)):
        await client.send_message(message.channel, 'hi')
        await Stickers.award(message.author.id, 'SecretHunter')

    elif message.content.startswith('{}bitter?'.format(prefix)):
        await client.send_message(message.channel, random.choice('It doesn\'t matter.|No I\'m fine xvu'.split('|')))
        await Stickers.award(message.author.id, 'SecretHunter')

    elif message.content.startswith('{}gibberish'.format(prefix)):
        await client.send_message(message.channel, gibberish())
        await Stickers.award(message.author.id, 'SecretHunter')

    elif message.content.startswith('{}miss'.format(prefix)):
        await client.send_message(message.channel, 'I miss {} :\'('.format(message.content.replace('{}miss '.format(prefix), '')))
        await Stickers.award(message.author.id, 'SecretHunter')

    elif message.content.startswith('{}pokemon'.format(prefix)):
        #https://cdn.discordapp.com/attachments/467397772044271617/471404564365705236/1532444999442.png
        emb = discord.Embed(title='A wild pokémon has appeared!',description='Guess the pokémom and type p!catch <pokémon> to catch it!', color=0xffd1dc)
        emb.set_image(url='https://cdn.discordapp.com/attachments/467397772044271617/471404564365705236/1532444999442.png')
        await client.send_message(message.channel, embed=emb)
        await Stickers.award(message.author.id, 'SecretHunter')
        
    elif message.content.upper().startswith('I MADE') or message.content.upper().startswith('TODAY I'):
        await client.send_message(message.channel, random.choice(['Ooh', gibberish()]))

    elif 'SEX' in message.content.upper() or 'EAR RAPE' in message.content.upper():
        await client.send_message(message.channel, discord.utils.get(client.get_all_emojis(), name='repent'))

    elif 'LOL' in message.content.upper().replace(' ',''):
        await client.add_reaction(message, discord.utils.get(client.get_all_emojis(), name='despacito'))
    
# -------------- Support Code -----------------
class YouMarriedError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors

class ThemMarriedError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors

async def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        print('error removing')
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def readproposals():
    with open('{}/proposals.pk'.format(settings.home_dir), 'rb') as f:
        proposals = pickle.load(f)
        return proposals

def readmarriages():
    with open('{}/directory.pk'.format(settings.home_dir), 'rb') as f:
        marriages = pickle.load(f)
        return marriages

def writemarriage(a, b):
    marriages = ''
    with open('{}/directory.pk'.format(settings.home_dir), 'rb') as f:
        marriages = pickle.load(f)
        marriages[a] = b
    with open('{}/directory.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(marriages, f)

def delmarriage(a):
    marriages = ''
    with open('{}/directory.pk'.format(settings.home_dir), 'rb') as f:
        marriages = pickle.load(f)
        del marriages[a]
    with open('{}/directory.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(marriages, f)

def propose(fro, to):
    proposals = '' #having issues with rb+, don't feel ,like messing with it
    with open('{}/proposals.pk'.format(settings.home_dir), 'rb') as f:
        proposals = pickle.load(f)
        proposals[fro] = to
    with open('{}/proposals.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(proposals, f)

def acceptmarriage(fro, to):
    proposals = ''
    with open('{}/proposals.pk'.format(settings.home_dir), 'rb') as f:
        proposals = pickle.load(f)
        del proposals[to]
    with open('{}/proposals.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(proposals, f)
    writemarriage(fro, to)

def readwmarriages():
    with open('{}/wishidirectory.pk'.format(settings.home_dir), 'rb') as f:
        wishimarriages = pickle.load(f)
        return wishimarriages

def writewmarriage(a):
    wishimarriages = '' #having issues with rb+, don't feel ,like messing with it
    with open('{}/wishidirectory.pk'.format(settings.home_dir), 'rb') as f:
        wishimarriages = pickle.load(f)
        try:
            wishimarriages[a]['marriages'] += 1
        except:
            wishimarriages[a] = {'marriages':1, 'anniversary' : datetime.now()}
    with open('{}/wishidirectory.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(wishimarriages, f)

def delwmarriage(a):
    wishimarriages = ''
    with open('{}/wishidirectory.pk'.format(settings.home_dir), 'rb') as f:
        wishimarriages = pickle.load(f)
        del wishimarriages[a]
    with open('{}/wishidirectory.pk'.format(settings.home_dir), 'wb') as f:
        pickle.dump(wishimarriages, f)

async def send_image(image, cli, channel, tran = None): #TODO: add lock to make this thread safe
    #with stuff_lock:
    try:
        if image.format == 'GIF':
            image.save('temp.gif', save_all=True, transparency=tran)
            await cli.send_file(channel, 'temp.gif')
            return
        bg = Image.new('RGBA', image.size)
        bg.paste(image, (0,0))
        bg.save('temp.png')
        await cli.send_file(channel, 'temp.png')
    except Exception as e:
        print('exception in send_image!')
        print('error: {}'.format(str(e)))
    finally:
        if not rosebud_configs.settings.suppress_loading_messages:
            for i in ['temp.png', 'temp.gif']:
                if os.path.isfile(i):
                    await silentremove(i)

def load_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def gibberish():
    return random.choice('shxjxh  sjdjdj  sjdksjxj  shxjxhx  djdjdh  dhdjdhshd  dhdjdh  dhsjdh  dhdjd  ahdjshdh'.split())

def premultiply(im):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            if a != 255:
                r = r * a // 255
                g = g * a // 255
                b = b * a // 255
                pixels[x, y] = (r, g, b, a)

def unmultiply(im):
    pixels = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = pixels[x, y]
            if a != 255 and a != 0:
                r = 255 if r >= a else 255 * r // a
                g = 255 if g >= a else 255 * g // a
                b = 255 if b >= a else 255 * b // a
                pixels[x, y] = (r, g, b, a)
           
client.run(settings.token)
