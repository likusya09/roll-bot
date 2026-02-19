import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Синхронизировано {len(synced)} слэш-команд.")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")

@bot.tree.command(name="roll", description="Случайное число от 1 до указанного")
async def roll(interaction: discord.Interaction, max_number: int):
    if max_number < 1:
        await interaction.response.send_message("❌ Число должно быть ≥ 1.", ephemeral=True)
        return

    await interaction.response.defer()
    result = random.randint(1, max_number)
    await interaction.followup.send(f"🎲 Выпало: **{result}** (из 1–{max_number})")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("⚠️ DISCORD_TOKEN не задан в переменных окружения!")
    else:
        bot.run(token)