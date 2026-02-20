import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import os

# === НАСТРОЙКИ ===
TOKEN = os.getenv("DISCORD_TOKEN")  # Для Replit/Railway
# Если локально — замени на: TOKEN = "твой_токен_здесь"

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

# === /кусь === (простой)
@bot.tree.command(name="кусь", description="Укусить указанного пользователя")
async def kus(interaction: discord.Interaction, target: discord.Member):
    name = interaction.user.display_name
    await interaction.response.send_message(f"{name} укусил(а) {target.mention}! 😼")

# === /куськ === (простой)
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
    await interaction.response.send_message(f"{name} укусил(а) {victim.mention}! 😼")

# === Вспомогательная функция для РП-атаки ===
def roll_attack():
    r = random.random()
    if r < 0.01:       # 1% — мегакусь
        return "megakus", "Мегакусь", -100
    elif r < 0.03:      # 20% крит (1% + 2% = 3%)
        return "crit", "Крит", -20
    elif r < 0.53:      # 50% попадание (3% → 53%)
        return "hit", "Попадание", -10
    elif r < 0.63:      # 10% промах (53% → 63%)
        return "miss", "Промах", 0
    else:               # оставшиеся 37% — тоже попадание (для надёжности)
        return "hit", "Попадание", -10

# === /кусьРП === (РП-версия с HP и склонением)
@bot.tree.command(name="кусьРП", description="Укусить указанного пользователя с РП-эффектами и HP")
async def kus_rp(interaction: discord.Interaction, target: discord.Member):
    author_name = interaction.user.display_name
    outcome, label, hp = roll_attack()

    # Подбираем глагол по полу/нейтрально (упрощённо: если имя оканчивается на 'а' или в списке — используем «а»)
    # Можно улучшить через role/ник, но для простоты — так:
    if interaction.user.display_name.endswith(("а", "я", "ь")) or interaction.user.display_name.lower() in ["лика", "боробка", "даника"]:
        verb_suffix = "а"
    else:
        verb_suffix = ""

    if outcome == "megakus":
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix}(а) наповал {target.mention}! (-100HP)"
    elif outcome == "crit":
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix}(а) кусочек от {target.mention}! (-20HP)"
    elif outcome == "hit":
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix}(а) {target.mention}! (-10HP)"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix}(а) по {target.mention}! (Целься лучше лузер)"

    await interaction.response.send_message(msg)

# === /куськРП === (РП-версия, рандом из чата)
@bot.tree.command(name="куськРП", description="Укусить случайного участника, писавшего здесь за последние 2 дня — с РП-эффектами")
async def kusk_rp(interaction: discord.Interaction):
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
        await interaction.response.send_message("Никто не писал здесь за последние 2 дня... 🐾", ephemeral=True)
        return

    victim = random.choice(list(authors))
    author_name = interaction.user.display_name

    # Склонение для автора
    if author_name.endswith(("а", "я", "ь")) or author_name.lower() in ["лика", "боробка", "даника"]:
        verb_suffix = "а"
    else:
        verb_suffix = ""

    outcome, label, hp = roll_attack()

    if outcome == "megakus":
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix}(а) наповал {victim.mention}! (-100HP)"
    elif outcome == "crit":
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix}(а) кусочек от {victim.mention}! (-20HP)"
    elif outcome == "hit":
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix}(а) {victim.mention}! (-10HP)"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix}(а) по {victim.mention}! (Целься лучше лузер)"

    await interaction.response.send_message(msg)

# === ЗАПУСК ===
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("⚠️ DISCORD_TOKEN не задан! Добавь его в Secrets (Replit) или Variables (Railway).")
