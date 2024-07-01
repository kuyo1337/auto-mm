import json
with open('config.json', 'r') as f:
    config = json.load(f)
fee = 1.08
your_discord_user_id = config['owner_id']
WorkspacePath = 'data'
bot_token = config['token']
ticket_channel = config['ticket_channel']
cancel = ['cancel', 'Cancel']
import asyncio
import random
import string
import time
import discord
from discord import colour
from discord.ext import commands
import json
import requests
import blockcypher
from pycoingecko import CoinGeckoAPI
import urllib3
import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from utils.checks import getConfig, updateConfig, staff_only
cg = CoinGeckoAPI()
api_key = config['api_key']
deals = {}

def epoch_to_formatted_date(epoch_timestamp):
    datetime_obj = datetime.datetime.fromtimestamp(epoch_timestamp)
    formatted_date = datetime_obj.strftime('%b %d %Y | %H:%M:%S')
    return formatted_date

def get_ltc_to_usd_price():
    response = cg.get_price(ids='litecoin', vs_currencies='usd')
    return response['litecoin']['usd']

def usd_to_satoshis(usd_amount):
    ltc_to_usd_price = get_ltc_to_usd_price()
    ltc_price_in_satoshis = 100000000
    satoshis_amount = int(usd_amount / ltc_to_usd_price * ltc_price_in_satoshis)
    return satoshis_amount

def satoshis_to_usd(satoshis_amount):
    ltc_to_usd_price = get_ltc_to_usd_price()
    ltc_price_in_satoshis = 100000000
    usd_amount = satoshis_amount / ltc_price_in_satoshis * ltc_to_usd_price
    return usd_amount

def satoshis_to_ltc(satoshis_amount):
    ltc_price_in_satoshis = 100000000
    ltc_amount = satoshis_amount / ltc_price_in_satoshis
    return ltc_amount

def ltc_to_satoshis(ltc_amount):
    ltc_price_in_satoshis = 100000000
    satoshis_amount = ltc_amount * ltc_price_in_satoshis
    return int(satoshis_amount)

def create_new_ltc_address():
    endpoint = f'https://api.blockcypher.com/v1/ltc/main/addrs?token={api_key}'
    response = requests.post(endpoint)
    data = response.json()
    new_address = data['address']
    private_key = data['private']
    return (new_address, private_key)

def get_address_balance(address):
    endpoint = f'https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance?token={api_key}'
    response = requests.get(endpoint)
    data = response.json()
    balance = data.get('balance', 0)
    unconfirmed_balance = data.get('unconfirmed_balance', 0)
    return (balance, unconfirmed_balance)

def send_ltc(private_key, recipient_address, amount):
    tx = blockcypher.simple_spend(from_privkey=private_key, to_address=recipient_address, to_satoshis=amount, api_key=api_key, coin_symbol='ltc')
    return tx
bot = commands.Bot(intents=discord.Intents.all(), command_prefix='<>:@:@')

def succeed(message):
    return discord.Embed(description=f':white_check_mark: {message}', color=8191851)

def info(message):
    return discord.Embed(description=f':information_source: {message}', color=5750527)

def fail(message):
    return discord.Embed(description=f':x: {message}', color=16739179)

def generate_fid():
    letters = string.ascii_letters
    return ''.join((random.choice(letters) for _ in range(10)))

class CopyPasteButtons(discord.ui.View):
    def __init__(self, dealid, ltcad):
        super().__init__(timeout=None)
        self.dealid = dealid
        self.ltcad = ltcad
        self.setup_buttons()

    def setup_buttons(self):
        button = discord.ui.Button(label='Copy LTC Address', custom_id='1', style=discord.ButtonStyle.primary)
        button.callback = self.ltc
        self.add_item(button)
        button = discord.ui.Button(label='Copy Deal Id', custom_id='3', style=discord.ButtonStyle.primary)
        button.callback = self.deal
        self.add_item(button)

    async def ltc(self, interaction: discord.Interaction):
        await interaction.response.send_message(ephemeral=True, content=self.ltcad)

    async def deal(self, interaction: discord.Interaction):
        await interaction.response.send_message(ephemeral=True, content=self.dealid)

class MiddleManButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.setup_buttons()

    def setup_buttons(self):
        button = discord.ui.Button(label='Crypto Middleman', custom_id='gemltc', style=discord.ButtonStyle.primary)
        button.callback = self.gemltc
        self.add_item(button)

    async def gemltc(self, interaction: discord.Interaction):
        DEALID = generate_fid()
        deals[DEALID] = {}
        deals[DEALID]['channel'] = await interaction.guild.create_text_channel(name=f'DEAL-{interaction.user.name}')
        overwrites = {interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        await deals[DEALID]['channel'].edit(overwrites=overwrites)
        deals[DEALID]['owner'] = interaction.user.id
        deals[DEALID]['usd'] = None
        deals[DEALID]['ltcid'] = None
        deals[DEALID]['ltcadd'] = None
        deals[DEALID]['stage'] = 'ltcid'
        data = getConfig(DEALID)
        data['id'] = DEALID
        data['owner'] = interaction.user.id
        updateConfig(DEALID, data)
        embed = discord.Embed(description=f'{DEALID}')
        embed1 = discord.Embed(title='**Middleman System 1.0.0**', description='Welcome to our Auto MM System - here we will process any deal involving Bitcoin', color=16225050)
        embed1.add_field(name='**How does it work?**', value='\n        Whoever is sending the Litecoin will send it to one of our secure wallets. Once the required amount of confirmations have been reached, we will ask the other user to provide the\n        item/asset/service to the user who sent the Cryptocurrency to us.', inline=False)
        embed1.add_field(name='**How many confirmations are required?**', value='\n        For Litecoin transactions we require 1 Network Confirmations, this is to ensure that nothing can go wrong with the payment.', inline=False)
        embed1.add_field(name='**What do I do if something goes wrong?**', value='\n        If you are ever confused or unsure, you may ping a member of <@&1214432308929495141> for assistance - we are always happy to assist!', inline=False)
        embedtwo = discord.Embed(title='Who are you dealing with?', description='\n        eg. 123456789012345678\n        ', color=16225050)
        await deals[DEALID]['channel'].send(embed=embed1)
        msg = await deals[DEALID]['channel'].send(embed=embed)
        deals[DEALID]['message'] = msg
        deals[DEALID]['embed'] = embed
        await deals[DEALID]['channel'].send(embed=embedtwo)
        await interaction.response.send_message(ephemeral=True, content=f"<#{deals[DEALID]['channel'].id}>")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Bot Ready')
    channel = await bot.fetch_channel(ticket_channel)
    embed = discord.Embed(title='**Auto - Cryptocurrency Services**', description='\n    The following rules must be followed - failure to abide may result in an instant ban. Staff will have independant thresholds to what is deemed completely innapropriate.\n    **Supported Currencies** 💱\n    Litecoin\n\n    **Service Fees** 💳\n    **0.02%** of deal\n\n    **How does it work?** ❔\n    Simply press the **\'Crypto Middleman\'** button below to create a ticket. We will ask you a series of questions in order for us to understand the deal.\n\n    > - What Cryptocurrency? (LTC)\n    > - Who are you dealing with? (dev id)\n    > - How much USD should the bot receive?\n\n    Once we understand what the deal is regarding, we will create a payment invoice for the sender, once the payment has securely been received we will tell both users to exchange assets, or whatever the deal is regarding. Once the product has been delivered the funds can be released for the other dealer to claim.\n\n    **Is this system safe?** 🛡️\n    This system is **100% secure**, we ensure every ticket has its own unique wallet to avoid any confliction. All wallet private keys are encrypted and securely stored, they are backed up and can be accessed if needed.\n      ', color=14971935)
    await channel.purge()
    await channel.send(embed=embed, view=MiddleManButtons())

async def final_middleman(sats, dealid):
    deal = deals[dealid]
    sats_fee = sats * fee
    data = getConfig(dealid)
    address, key = create_new_ltc_address()
    data['addy'] = address
    data['private'] = key
    updateConfig(dealid, data)
    amt_usd = satoshis_to_usd(sats_fee)
    amt_ltc = satoshis_to_ltc(sats_fee)
    embed = discord.Embed(title='**Payment Invoice**', description=f'This transaction is approximately **${amt_usd}**, however to ensure we can validate your payment successfully please copy and paste the value of **{amt_ltc}** and send it to our address.', color=16225050)
    embed.add_field(name='**Payment Address**', value=f'`{address}`', inline=False)
    embed.add_field(name='**Amount Litecoin**', value=f'`{amt_ltc}`', inline=False)
    embed.add_field(name='**Amount USD**', value=f'`{amt_usd}`', inline=False)
    embedtwo = discord.Embed(color=16225050)
    gay = embedtwo.set_author(name='Waiting for transaction...', icon_url='https://cdn.discordapp.com/emojis/1098069475573633035.gif?size=96&quality=lossless')
    await deal['channel'].send(embed=embed)
    await deal['channel'].send(f'{address}')
    await deal['channel'].send(embed=succeed('Payment Confirmed!'))
    await deal['channel'].send(embed=succeed('Should we release payement?'), view=ReleaseButtons(dealid=dealid))

@bot.event
async def on_message(message: discord.Message):
    if message.author.id == bot.user.id:
        return

    for dealid in deals:
        deal = deals[dealid]
        if deal['channel'].id == message.channel.id:
            stage = deal['stage']
            data = getConfig(dealid)

            if not stage == 'ltcid' or message.content in cancel:
                if message.author.id == data['owner']:
                    channel = deals[dealid]['channel']
                    await channel.send('Cancelled Deal')
                    deals[dealid]['stage'] = 'end'
                    await channel.edit(name=f'cancelled-{dealid}')
                    await asyncio.sleep(30)
                    await channel.delete()
                return

            if stage == 'ltcid':
                deals[dealid]['ltcid'] = message.content
                user1_id = data['owner']
                user1 = message.guild.get_member(user1_id)
                user_id = int(message.content)
                user = message.guild.get_member(user_id)
                channel = deals[dealid]['channel']
                overwrites = {
                    user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    user1: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    message.guild.default_role: discord.PermissionOverwrite(read_messages=False)
                }
                await channel.edit(overwrites=overwrites)
                await channel.send('**Terms of Service (ToS)**\n\n**Server Ownership Transfer:**\n   - 🚚 When selling server ownership, both parties must screen record the transfer process for documentation purposes.\n\n **Buying Codes (Nitro, Promo, Redeem, VCC, Tokens, etc.):**\n\n   - **For Buyers:**\n     - 🎥 Turn on screen recording before the seller sends Nitro gift links, codes, VCC, or tokens in DMs.\n     - Continue recording until you successfully claim the code/VCC.\n     - For tokens and promos, if you want to release after check, record the screen during checking promos/tokens.\n\n   - **For Sellers:**\n     - 🤝 Confirm with the buyer if they are ready to record their screen before sharing any codes.\n     - Do not share anything without the buyer\'s confirmation.\n\n**Exchange Deals:**\n   - 💰 Make sure to log in to your account and confirm that you have received the current amount before releasing the asset to avoid losses.\n\n **Member Deals:**\n   - 📊 If you\'re buying members for your server, take a screenshot showing the current number of members. Also, set a welcome message for bot detection.\n\n **Important Note:**\n   - ❗ Failure to adhere to these procedures may result in consequences for both parties.\n\n- 🗣️ Discuss ToS and warranty in DM or in a ticket before payment. Bot would not ask about this, so do this by your own.\n\n   - 🚨 Ping support team if you face any problems during the deal.')
                embex = discord.Embed(
                    title='**Crypto MM**',
                    description='>>> Welcome to our automated cryptocurrency Middleman system! Your cryptocurrency will be stored securely till the deal is completed. The system ensures the security of both users, by securely storing the funds until the deal is complete and confirmed by both parties.',
                    colour=16225050
                )
                embex1 = discord.Embed(
                    title='**Please Read!**',
                    description='Please check deal info , confirm your deal and discuss about tos and warranty of that product. Ensure all conversations related to the deal are done within this ticket. Failure to do so may put you at risk of being scammed.',
                    colour=16225050
                )
                await channel.send(content=f'<@{user_id}><@{user1_id}>', embed=embex)
                await channel.send(embed=embex1)
                data['owner'] = 0
                updateConfig(dealid, data)
                embed = discord.Embed(
                    title='User Identification',
                    description='**Sender** - Providing Litecoin to bot\n**Reciever** - Receiving Litecoin after deal is completed',
                    color=16225050
                )
                embed.add_field(name='**Sender**', value='None', inline=True)
                embed.add_field(name='**Reciever**', value='None', inline=True)
                msg1 = await channel.send(embed=info(f'<@{user_id}> Was Added To The Ticket'))
                await msg1.edit(embed=embed, view=SenButtons(dealid=dealid, mnk=msg1.id))

            if stage == 'usd':
                if message.author.id == data['owner']:
                    try:
                        amount = float(message.content)
                        if amount <= 0.050:
                            await message.reply(embed=fail('Must Be Over 0.050$'))
                            break
                        deals[dealid]['usd'] = amount
                        deals[dealid]['stage'] = 'ltcadd'
                        amt = usd_to_satoshis(amount)
                        amt1 = satoshis_to_ltc(amt)
                        data['amount'] = amt1
                        updateConfig(dealid, data)
                        embed = discord.Embed(
                            title='**Confirm Amount**',
                            description=f'Are you sure we are expected to receive `{amount}`$ LTC',
                            color=16225050
                        )
                        await fail(embed=fail(f"<@{deal['reciev']}> Enter Correct LTC Address"))
                    except ValueError:
                        await fail(embed=fail('Remove The $ Symbol'))
                    finally:
                        break

            if stage == 'release':
                tx = send_ltc(key, addy, ltc_to_satoshis(data['amount']))
                await succeed(embed=succeed(f'Transaction ID: [{tx}](https://blockchair.com/litecoin/transaction/{tx})'))
                break

            if stage == 'cancel' and 'reciev' in data:
                try:
                    tx = send_ltc(key, addy, usd_to_satoshis(data['amount']))
                    await succeed(embed=succeed(f'Transaction ID: [{tx}](https://blockchair.com/litecoin/transaction/{tx})'))
                except Exception as e:
                    await fail(embed=fail(f"<@{deal['reciev']}> Enter Correct LTC Address"))
                finally:
                    break
class conButtons(discord.ui.View):
    def __init__(self, dealid):
        super().__init__(timeout=None)
        self.dealid = dealid
        self.channel = deals[dealid]['channel']
        self.setup_buttons()

    def setup_buttons(self):
        button = discord.ui.Button(label='Confirm', custom_id='sede', style=discord.ButtonStyle.green)
        button.callback = self.sendr1
        self.add_item(button)
        button = discord.ui.Button(label='Incorrect', custom_id='rece', style=discord.ButtonStyle.red)
        button.callback = self.recvr1
        self.add_item(button)

    async def sendr1(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        amt = data['amount']
        amt1 = ltc_to_satoshis(amt)
        amt2 = satoshis_to_usd(amt1)
        if interaction.user.id == data['reciev']:
            deals[self.dealid]['stage'] = 'ltcadd'
            embed = discord.Embed(title='**Deal Amount**', description=f'>>> Both users have confirmed that we are expected to receive `{amt2}`$ USD.', color=16225050)
            await interaction.response.send_message(embed=embed)
            asyncio.create_task(final_middleman(amt1, self.dealid))
            return
        else:
            await interaction.response.send_message('**You are not Reciever**', ephemeral=True)

    async def recvr1(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        if interaction.user.id == data['reciev']:
            deals[self.dealid]['stage'] = 'usd'
            await interaction.response.send_message(embed=succeed('Ammount of usd to hold'))
        else:  
            await interaction.response.send_message('**You are not Reciever**', ephemeral=True)

class SenButtons(discord.ui.View):
    def __init__(self, dealid, mnk):
        super().__init__(timeout=None)
        self.dealid = dealid
        self.msg_id = mnk
        self.channel = deals[dealid]['channel']
        self.setup_buttons()

    def setup_buttons(self):
        button = discord.ui.Button(label='I am Sender', custom_id='sed', style=discord.ButtonStyle.gray)
        button.callback = self.sendr
        self.add_item(button)
        button = discord.ui.Button(label='I am Reciever', custom_id='rec', style=discord.ButtonStyle.gray)
        button.callback = self.recvr
        self.add_item(button)
        button = discord.ui.Button(label='Done', custom_id='fin', style=discord.ButtonStyle.gray)
        button.callback = self.done
        self.add_item(button)
        button = discord.ui.Button(label='Reset', custom_id='fien', style=discord.ButtonStyle.red)
        button.callback = self.reset
        self.add_item(button)

    async def sendr(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        data['owner'] = interaction.user.id
        updateConfig(self.dealid, data)
        if data['owner']!= data['reciev']:
            data['owner'] = interaction.user.id
            updateConfig(self.dealid, data)
            if data['reciev'] == 1:
                embed = discord.Embed(title='User Identification', description='**Sender** - Providing Litecoin to bot\n**Reciever** - Recieving Litecoin after deal is completed', color=16225050)
                embed.add_field(name='**Sender**', value=f"<@{data['owner']}>", inline=True)
                embed.add_field(name='**Reciever**', value='None', inline=True)
                message = await self.channel.fetch_message(self.msg_id)
                await message.edit(embed=embed)
                await interaction.response.send_message(f"**<@{data['owner']}> Marked as Sender**", ephemeral=True)
            else:  
                embed = discord.Embed(title='User Identification', description='**Sender** - Providing Litecoin to bot\n**Reciever** - Recieving Litecoin after deal is completed', color=16225050)
                embed.add_field(name='**Sender**', value=f"<@{data['owner']}>", inline=True)
                embed.add_field(name='**Reciever**', value=f"<@{data['reciev']}>", inline=True)
                message = await self.channel.fetch_message(self.msg_id)
                await message.edit(embed=embed)
                await interaction.response.send_message(f"**<@{data['owner']}> Marked as Sender**", ephemeral=True)
        else:  
            await interaction.response.send_message('**You are already marked as reciver**', ephemeral=True)

    async def recvr(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        data['reciev'] = interaction.user.id
        updateConfig(self.dealid, data)
        if data['reciev']!= data['owner']:
            data['reciev'] = interaction.user.id
            updateConfig(self.dealid, data)
            if data['owner'] == 0:
                embed = discord.Embed(title='User Identification', description='**Sender** - Providing Litecoin to bot\n**Reciever** - Recieving Litecoin after deal is completed', color=16225050)
                embed.add_field(name='**Sender**', value='None', inline=True)
                embed.add_field(name='**Reciever**', value=f"<@{data['reciev']}>", inline=True)
                message = await self.channel.fetch_message(self.msg_id)
                await message.edit(embed=embed)
                await interaction.response.send_message(f"**<@{data['reciev']}> Marked as Reciever**", ephemeral=True)
            else:  
                embed = discord.Embed(title='User Identification', description='**Sender** - Providing Litecoin to bot\n**Reciever** - Recieving Litecoin after deal is completed', color=16225050)
                embed.add_field(name='**Sender**', value=f"<@{data['owner']}>", inline=True)
                embed.add_field(name='**Reciever**', value=f"<@{data['reciev']}>", inline=True)
                message = await self.channel.fetch_message(self.msg_id)
                await message.edit(embed=embed)
                await interaction.response.send_message(f"**<@{data['reciev']}> Marked as Reciever**", ephemeral=True)
        else:  
            await interaction.response.send_message('**You are already marked as Sender**', ephemeral=True)

    async def done(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        if data['reciev'] == 1:
            await interaction.response.send_message('**Must specify reciever**', ephemeral=True)
        if data['owner'] == 0:
            await interaction.response.send_message('**must specify sender**', ephemeral=True)
        if data['owner'] == data['reciev']:
            await interaction.response.send_message('**You cant be both sender and reciever**', ephemeral=True)
        if interaction.user.id == data['owner']:
            message = await self.channel.fetch_message(self.msg_id)
            await message.edit(view=None)
            await interaction.response.send_message(embed=succeed('Ammount of usd to hold'))
            deals[self.dealid]['stage'] = 'usd'
        else:  
            await interaction.response.send_message(embed=fail('Only Sender can Confirm'), ephemeral=True)

    async def reset(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        data['reciev'] = 1
        data['owner'] = 0
        updateConfig(self.dealid, data)
        embed = discord.Embed(title='User Identification', description='**Sender** - Providing Litecoin to bot\n**Reciever** - Recieving Litecoin after deal is completed', color=16225050)
        embed.add_field(name='**Sender**', value='None', inline=True)
        embed.add_field(name='**Reciever**', value='None', inline=True)
        message = await self.channel.fetch_message(self.msg_id)
        await message.edit(embed=embed)
        await interaction.response.send_message(embed=succeed('Sucessfully reset'), ephemeral=True)

class ReleaseButtons(discord.ui.View):
    def __init__(self, dealid):
        super().__init__(timeout=None)
        self.dealid = dealid
        self.setup_buttons()

    def setup_buttons(self):
        button = discord.ui.Button(label='Release', custom_id='join', style=discord.ButtonStyle.green)
        button.callback = self.release
        self.add_item(button)
        button = discord.ui.Button(label='cancel', custom_id='joins', style=discord.ButtonStyle.danger)
        button.callback = self.cancel
        self.add_item(button)

    async def release(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        own_id = data['owner']
        if interaction.user.id == own_id:
            deals[self.dealid]['stage'] = 'release'
            await interaction.response.send_message(embed=succeed('**Releasing Litecoin**\n~ `Send ltc adress below`'))
            await interaction.response.send_message('**CHECK THE ADDRESS TWICE BEFORER SENDING**')
        else:  
            await interaction.response.send_message(embed=fail('You Are not the sender of this deal'))

    async def cancel(self, interaction: discord.Interaction):
        data = getConfig(self.dealid)
        own_id = data['owner']
        await interaction.response.send_message(embed=succeed('Contact Owner To get back payement'))

@bot.tree.command(name='get_private_key', description='Get The Private Key Of A Wallet')
async def GETKEY(interaction: discord.Interaction, deal_id: str):
    if interaction.user.id == your_discord_user_id:
        key = deals[deal_id]['key']
        await interaction.response.send_message(embed=info(key))
    else:  
        await interaction.response.send_message(embed=fail('Only Admins Can Do This'))

@bot.tree.command(name='get_wallet_balance', description='Get The Balance Of A Wallet')
async def GETBAL(interaction: discord.Interaction, address: str):
    balsats, unbalsats = get_address_balance(address)
    balusd = satoshis_to_usd(balsats)
    balltc = satoshis_to_ltc(balsats)
    unbalusd = satoshis_to_usd(unbalsats)
    unballtc = satoshis_to_ltc(unbalsats)
    embed = discord.Embed(title=f'Address {address}', description=f'**Balance**\n\nUSD: {balusd}\nLTC: {balltc}\nSATS: {balsats}\n\n**Unconfirmed Balance**\n\nUSD: {unbalusd}\nLTC: {unballtc}\nSATS: {unbalsats}')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='send', description='Send Litecoin to a wallet')
@staff_only()
async def SEND(interaction: discord.Interaction, deal_id: str, addy: str):
    data = getConfig(deal_id)
    onr = data['reciev']
    amount = data['amount']
    key = data['private']
    tx = send_ltc(key, addy, ltc_to_satoshis(amount))
    await interaction.response.send_message(embed=succeed(f'Sent {amount} to {addy}'))
bot.run(bot_token)