import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    await bot.tree.sync()

# /кусь @пользователь
@bot.tree.command(name="кусь", description="Укусить указанного пользователя")
async def kus(interaction: discord.Interaction, target: discord.Member):
    name = interaction.user.display_name
    await interaction.response.send_message(f"{name} укусила {target.mention}! 😼")

# /куськ — рандом из писавших за 2 дня
@bot.tree.command(name="куськ", description="Укусить случайного участника, писавшего здесь за последние 2 дня")
async def kusk(interaction: discord.Interaction):
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("❌ Только в текстовых каналах.", ephemeral=True)
        return

    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    authors = set()

    async for msg in channel.history(limit=1000, after=two_days_ago):
        if not msg.author.bot and msg.author != bot.user:
            authors.add(msg.author)

    if not authors:
        await interaction.response.send_message("Никто не писал тут 2 дня... 🐾", ephemeral=True)
        return

    victim = random.choice(list(authors))
    name = interaction.user.display_name
    await interaction.response.send_message(f"{name} укусила {victim.mention}! 😼")

# Запуск
bot.run(TOKEN)
