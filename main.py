import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import os

# === ТОКЕН ===
TOKEN = os.getenv("DISCORD_TOKEN")  # Для Replit/Railway
# Если запускаешь локально — замени на: TOKEN = "твой_токен_здесь"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Синхронизировано {len(synced)} слэш-команд.")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")

# === /roll ===
@bot.tree.command(name="roll", description="Случайное число от 1 до указанного")
async def roll(interaction: discord.Interaction, max_number: int):
    if max_number < 1:
        await interaction.response.send_message("❌ Число должно быть ≥ 1.", ephemeral=True)
        return
    await interaction.response.defer()
    result = random.randint(1, max_number)
    await interaction.followup.send(f"🎲 Выпало: **{result}** (из 1–{max_number})")

# === /кусь ===
@bot.tree.command(name="кусь", description="Укусить указанного пользователя")
async def kus(interaction: discord.Interaction, target: discord.Member):
    name = interaction.user.display_name
    await interaction.response.send_message(f"{name} укусила {target.mention}! 😼")

# === /куськ ===
@bot.tree.command(name="куськ", description="Укусить случайного участника, писавшего здесь за последние 2 дня")
async def kusk(interaction: discord.Interaction):
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("❌ Эта команда работает только в текстовых каналах.", ephemeral=True)
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

# === ЗАПУСК ===
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("⚠️ DISCORD_TOKEN не задан! Добавь его в Secrets (Replit) или Variables (Railway).")
