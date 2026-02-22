import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import os
import re

# === ТОКЕН ===
TOKEN = os.getenv("DISCORD_TOKEN")  # Для Replit/Railway
# Если локально — замени на: TOKEN = "твой_токен_здесь"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СКЛОНЕНИЯ ===
def get_verb_suffix(name: str) -> str:
    """Возвращает 'а', если имя женское, иначе '' (для глаголов: укусил → укусила)."""
    clean = re.sub(r"[^a-zа-яё0-9]", "", name.lower())
    female_keywords = {
        "yuukou", "elena", "hanali", "bopobka", "dannika", "alina", "alinca", "alinka",
        "ellie", "ana", "anastasia", "amo", "kurumi", "medeia", "bonni", "diana",
        "anya", "solnishko", "bonniblu", "лика", "аня", "даника", "боробка"
    }
    if clean.endswith(("а", "я", "ь")) or any(kw in clean for kw in female_keywords):
        return "а"
    return ""

def get_ushel_suffix(name: str) -> str:
    """Возвращает 'ла', если имя женское, иначе '' (для глагола: ушёл → ушла)."""
    clean = re.sub(r"[^a-zа-яё0-9]", "", name.lower())
    female_keywords = {
        "yuukou", "elena", "hanali", "borobka", "dannika", "alina", "alinca", "alinka",
        "ellie", "ana", "anastasia", "amo", "kurumi", "medeia", "bonni", "diana",
        "anya", "solnishko", "bonniblu", "лика", "аня", "даника", "боробка"
    }
    if clean.endswith(("а", "я", "ь")) or any(kw in clean for kw in female_keywords):
        return "ла"
    return ""

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
    result = random.randint(1, max_number)
    await interaction.response.send_message(f"🎲 Выпало: **{result}** (из 1–{max_number})")

# === /кусь ===
@bot.tree.command(name="кусь", description="Укусить указанного пользователя")
async def kus(interaction: discord.Interaction, target: discord.Member):
    name = interaction.user.display_name
    suffix = get_verb_suffix(name)
    await interaction.response.send_message(f"{name} укусил{suffix} {target.mention}! 😼")

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
    suffix = get_verb_suffix(name)
    await interaction.response.send_message(f"{name} укусил{suffix} {victim.mention}! 😼")

# === Вспомогательная функция для броска ===
def roll_attack():
    r = random.random()
    if r < 0.01:       # 1% — мегакусь
        return "megakus"
    elif r < 0.21:      # 20% — крит
        return "crit"
    elif r < 0.71:      # 50% — попадание
        return "hit"
    elif r < 0.81:      # 10% — промах
        return "miss"
    elif r < 0.90:      # 9% — контратака
        return "counter"
    elif r < 0.95:      # 5% — падение
        return "fail"
    else:               # 5% — зелье
        return "potion"

# === /кусьрп ===
@bot.tree.command(name="кусьрп", description="Укусить указанного пользователя с РП-эффектами и HP")
async def kus_rp(interaction: discord.Interaction, target: discord.Member):
    author = interaction.user
    author_name = author.display_name
    target_name = target.display_name
    verb_suffix = get_verb_suffix(author_name)

    outcome = roll_attack()

    if outcome == "megakus":
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix} наповал {target.mention}! (-100HP)"
    elif outcome == "crit":
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix} кусочек от {target.mention}! (-20HP)"
    elif outcome == "hit":
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix} {target.mention}! (-10HP)"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix} по {target.mention}! (Целься лучше лузер!)"
    elif outcome == "counter":
        ushel_suffix = get_ushel_suffix(target_name)
        ukusil_suffix = get_verb_suffix(target_name)
        msg = f"(Парирование)! {target.mention} Ловко уш{ushel_suffix} от атаки и укусил{ukusil_suffix} {author_name}! (-10HP)"
    elif outcome == "fail":
        msg = f"(Неудача)! {author_name} (-5HP) Упал{verb_suffix} моськой в лужу, когда хотел{verb_suffix} укусить {target.mention}!"
    elif outcome == "potion":
        msg = f"(Корм)! {author_name} (+5HP) Решил{verb_suffix} поесть вискаса, а не кусить {target.mention}!"

    await interaction.response.send_message(msg)

# === /куськрп ===
@bot.tree.command(name="куськрп", description="Укусить случайного участника, писавшего здесь за последние 2 дня — с РП-эффектами")
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
    author = interaction.user
    author_name = author.display_name
    victim_name = victim.display_name
    verb_suffix = get_verb_suffix(author_name)

    outcome = roll_attack()

    if outcome == "megakus":
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix} наповал {victim.mention}! (-100HP)"
    elif outcome == "crit":
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix} кусочек от {victim.mention}! (-20HP)"
    elif outcome == "hit":
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix} {victim.mention}! (-10HP)"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix} по {victim.mention}! (Целься лучше лузер!)"
    elif outcome == "counter":
        ushel_suffix = get_ushel_suffix(victim_name)
        ukusil_suffix = get_verb_suffix(victim_name)
        msg = f"(Парирование)! {victim.mention} Ловко уш{ushel_suffix} от атаки и укусил{ukusil_suffix} {author_name}! (-10HP)"
    elif outcome == "fail":
        msg = f"(Неудача)! {author_name} (-5HP) Упал{verb_suffix} моськой в лужу, когда хотел{verb_suffix} укусить {victim.mention}!"
    elif outcome == "potion":
        msg = f"(Корм)! {author_name} (+5HP) Решил{verb_suffix} поесть вискаса, а не кусить {victim.mention}!"

    await interaction.response.send_message(msg)

# === ЗАПУСК ===
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("⚠️ DISCORD_TOKEN не задан! Добавь его в Secrets (Replit) или Variables (Railway).")

