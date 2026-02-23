import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import os
import re
import json

# === ТОКЕН ===
TOKEN = os.getenv("DISCORD_TOKEN")  # Для Replit/Railway

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === ФАЙЛ ДЛЯ ХРАНЕНИЯ HP ===
HP_FILE = "hp.json"

def load_hp():
    if os.path.exists(HP_FILE):
        with open(HP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_hp(data):
    with open(HP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def get_ushel_form(name: str) -> str:
    """Возвращает 'ушла' если имя женское, иначе 'ушёл'."""
    clean = re.sub(r"[^a-zа-яё0-9]", "", name.lower())
    female_keywords = {
        "yuukou", "elena", "hanali", "bopobka", "dannika", "alina", "alinca", "alinka",
        "ellie", "ana", "anastasia", "amo", "kurumi", "medeia", "bonni", "diana",
        "anya", "solnishko", "bonniblu", "лика", "аня", "даника", "боробка"
    }
    if clean.endswith(("а", "я", "ь")) or any(kw in clean for kw in female_keywords):
        return "ушла"
    return "ушёл"

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

# === /hp — посмотреть здоровье ===
@bot.tree.command(name="hp", description="Посмотреть своё HP")
async def check_hp(interaction: discord.Interaction):
    hp_data = load_hp()
    user_id = str(interaction.user.id)
    hp = hp_data.get(user_id, 100)
    await interaction.response.send_message(f"🩸 {interaction.user.display_name}: **{hp} HP**")

# === /битва — сбросить HP всех участников ===
@bot.tree.command(name="битва", description="Начать новую битву (сбросить HP до 100)")
async def reset_battle(interaction: discord.Interaction):
    save_hp({})
    await interaction.response.send_message("⚔️ Новая битва началась! Все получили **100 HP**.")

# === Вспомогательная функция для изменения HP ===
def apply_hp_change(user_id: str, delta: int):
    hp_data = load_hp()
    current = hp_data.get(user_id, 100)
    new_hp = current + delta
    hp_data[user_id] = new_hp
    save_hp(hp_data)
    return new_hp

# === Вспомогательная функция для броска ===
def roll_attack():
    r = random.random()
    if r < 0.01:       # 1% — мегакусь
        return "megakus"
    elif r < 0.16:      # 15% — крит
        return "crit"
    elif r < 0.66:      # 50% — попадание
        return "hit"
    elif r < 0.78:      # 12% — промах
        return "miss"
    elif r < 0.90:      # 12% — контратака
        return "counter"
    elif r < 0.95:      # 5% — падение
        return "fail"
    else:               # 5% — зелье
        return "potion"

# === /кусь === (без HP, как у тебя)
@bot.tree.command(name="кусь", description="Укусить указанного пользователя")
async def kus(interaction: discord.Interaction, target: discord.Member):
    name = interaction.user.display_name
    suffix = get_verb_suffix(name)
    await interaction.response.send_message(f"{name} укусил{suffix} {target.mention}! 😼")

# === /куськ === (без HP, как у тебя)
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

# === /кусьрп с HP ===
@bot.tree.command(name="кусьрп", description="Укусить указанного пользователя с РП-эффектами и HP")
async def kus_rp(interaction: discord.Interaction, target: discord.Member):
    author = interaction.user
    author_name = author.display_name
    target_name = target.display_name
    author_id = str(author.id)
    target_id = str(target.id)
    verb_suffix = get_verb_suffix(author_name)

    outcome = roll_attack()

    if outcome == "megakus":
        new_hp = apply_hp_change(target_id, -100)
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix} наповал {target.mention}! (-100HP)\n🩸 {target_name}: {new_hp} HP"
    elif outcome == "crit":
        new_hp = apply_hp_change(target_id, -20)
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix} кусочек от {target.mention}! (-20HP)\n🩸 {target_name}: {new_hp} HP"
    elif outcome == "hit":
        new_hp = apply_hp_change(target_id, -10)
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix} {target.mention}! (-10HP)\n🩸 {target_name}: {new_hp} HP"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix} по {target.mention}! (Целься лучше лузер!)"
    elif outcome == "counter":
        ushel_form = get_ushel_form(target_name)
        ukusil_suffix = get_verb_suffix(target_name)
        new_hp = apply_hp_change(author_id, -10)
        msg = f"(Парирование)! {target.mention} Ловко {ushel_form} от атаки и укусил{ukusil_suffix} {author_name}! (-10HP)\n🩸 {author_name}: {new_hp} HP"
    elif outcome == "fail":
        new_hp = apply_hp_change(author_id, -5)
        msg = f"(Неудача)! {author_name} (-5HP) Упал{verb_suffix} моськой в лужу, когда хотел{verb_suffix} укусить {target.mention}!\n🩸 {author_name}: {new_hp} HP"
    elif outcome == "potion":
        new_hp = apply_hp_change(author_id, +5)
        msg = f"(Корм)! {author_name} (+5HP) Решил{verb_suffix} поесть вискаса, а не кусить {target.mention}!\n🩸 {author_name}: {new_hp} HP"

    # Проверка смерти
    if outcome in ("megakus", "crit", "hit", "counter") and new_hp <= 0:
        msg += f"\n💀 **{target_name} повержен(а)!**\n🏆 Победитель: **{author_name}**!"
    if outcome in ("fail", "potion") and new_hp <= 0:
        msg += f"\n💀 **{author_name} погиб(ла) от неудачи!**"

    await interaction.response.send_message(msg)

# === /куськрп с HP ===
@bot.tree.command(name="куськрп", description="Укусить случайного участника, писавшего здесь за последние 2 дня — с РП-эффектами и HP")
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
    author_id = str(author.id)
    victim_id = str(victim.id)
    verb_suffix = get_verb_suffix(author_name)

    outcome = roll_attack()

    if outcome == "megakus":
        new_hp = apply_hp_change(victim_id, -100)
        msg = f"(Мегакусь)! {author_name} Свалил{verb_suffix} наповал {victim.mention}! (-100HP)\n🩸 {victim_name}: {new_hp} HP"
    elif outcome == "crit":
        new_hp = apply_hp_change(victim_id, -20)
        msg = f"(Крит)! {author_name} Оторвал{verb_suffix} кусочек от {victim.mention}! (-20HP)\n🩸 {victim_name}: {new_hp} HP"
    elif outcome == "hit":
        new_hp = apply_hp_change(victim_id, -10)
        msg = f"(Попадание)! {author_name} Укусил{verb_suffix} {victim.mention}! (-10HP)\n🩸 {victim_name}: {new_hp} HP"
    elif outcome == "miss":
        msg = f"(Промах)! {author_name} Не попал{verb_suffix} по {victim.mention}! (Целься лучше лузер!)"
    elif outcome == "counter":
        ushel_form = get_ushel_form(victim_name)
        ukusil_suffix = get_verb_suffix(victim_name)
        new_hp = apply_hp_change(author_id, -10)
        msg = f"(Парирование)! {victim.mention} Ловко {ushel_form} от атаки и укусил{ukusil_suffix} {author_name}! (-10HP)\n🩸 {author_name}: {new_hp} HP"
    elif outcome == "fail":
        new_hp = apply_hp_change(author_id, -5)
        msg = f"(Неудача)! {author_name} (-5HP) Упал{verb_suffix} моськой в лужу, когда хотел{verb_suffix} укусить {victim.mention}!\n🩸 {author_name}: {new_hp} HP"
    elif outcome == "potion":
        new_hp = apply_hp_change(author_id, +5)
        msg = f"(Корм)! {author_name} (+5HP) Решил{verb_suffix} поесть вискаса, а не кусить {victim.mention}!\n🩸 {author_name}: {new_hp} HP"

    # Проверка смерти
    if outcome in ("megakus", "crit", "hit", "counter") and new_hp <= 0:
        msg += f"\n💀 **{victim_name} повержен(а)!**\n🏆 Победитель: **{author_name}**!"
    if outcome in ("fail", "potion") and new_hp <= 0:
        msg += f"\n💀 **{author_name} погиб(ла) от неудачи!**"

    await interaction.response.send_message(msg)

# === ЗАПУСК ===
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("⚠️ DISCORD_TOKEN не задан!")

