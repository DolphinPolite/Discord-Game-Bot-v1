import discord
from discord import Embed
from discord.ui import Button, View
from discord.ext import commands, tasks
from itertools import cycle 
from dotenv import load_dotenv
import os
from game import Game
import sqlite3

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

bot_status = cycle(["1", "2", "3", "4"])

load_dotenv()

SPEELS = []

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))

@client.event
async def on_ready():
    channel = client.get_channel(1007625208443703366)
    await channel.send("Yor'ue Bluetooth Device Is Connected Successfully!")
    change_status.start()

    try:
        synced_commands = await client.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occurred", e)

@client.tree.command(name="fight", description="You can fight against your friend or something")
async def pvp(interaction: discord.Interaction, player2: discord.Member):
    channel = client.get_channel(interaction.channel.id)

    await interaction.response.send_message(f"You invited <@{player2.id}> to play.", ephemeral=True, view=Game(MainInteraction=interaction, player1=interaction.user, player2=player2, usingFor="HOST"))
    await channel.send(f"<@{player2.id}>, you invited to a game with <@{interaction.user.id}>!", view=Game(MainInteraction=interaction, player1=interaction.user, player2=player2, usingFor="ACorReF"))

@client.tree.command(name="energy", description="Set your energy")
async def energySet(interaction: discord.Interaction, number: int):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(f"UPDATE Users SET EnergyAmount = ? WHERE guild_id = ? AND user_id = ?", (number, interaction.guild.id, interaction.user.id))
    connection.commit()
    connection.close()
    await interaction.response.send_message("Got'cha!", ephemeral=True)

@client.command()
async def yaz(ctx):
    await ctx.reply(ctx.channel.id)

@client.command(aliases=["Deneme", "A"]) 
async def fight(ctx, member: discord.Member):
    await ctx.reply(ctx.channel.id)

@client.command()
async def adana(ctx):
    embed = discord.Embed(
        title="başlık",
        description="açıklama",
        color=discord.Colour.brand_green()
    )

    embed.add_field(name="Olanlar:", value="- ağaç çarptı uzay taşı uçtu yıldız kaydı\n- Bi daha olmayacak sakin olun\n\n", inline=False)
    embed.add_field(name="YETENEKLERİN", value="**Deneme1**: işte öyle şöyle böyle olacak işte gardaş böyle yap şöyle olsun deneme msajı falan fistan\n\n**Denem2**: Adana merkez patlıyo herkes\n\n**deneem3**: NE BİLEYİM HAYAT NEDİR NE DEĞİLDİR BİLMİYORUM BANA PAPATYA ÇAYI LAZIM ĞĞĞĞ")
    embed.add_field(name="RAKİBİN YETENEKLERİ", value="**Deneme1**: işte öyle şöyle böyle olacak işte gardaş böyle yap şöyle olsun deneme msajı falan fistan\n\n**Denem2**: Adana merkez patlıyo herkes\n\n**deneem3**: NE BİLEYİM HAYAT NEDİR NE DEĞİLDİR BİLMİYORUM BANA PAPATYA ÇAYI LAZIM ĞĞĞĞ")
    embed.add_field(inline=False, name="", value="")
    embed.add_field(name="DURUMUN", value="""```fix
deneme
```""")
    
    embed.set_image(url="https://www.youtube.com/watch?v=Xm8laEsj_TQ&list=RDXm8laEsj_TQ&start_radio=1")

    await ctx.channel.send(embed=embed)


client.run(os.getenv("TOKEN"))