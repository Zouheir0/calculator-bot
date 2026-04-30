import discord
from discord.ext import commands
from discord import app_commands
import os
import json

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# FILE STORAGE
# =========================
FILE = "privates.json"

def load_privates():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return {}

def save_privates(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

privates = load_privates()

# =========================
# DRILLS
# =========================
drills = {
    "Uranium Drill": {"price": 437.5e9, "rate": 12500},
    "Fusion Drill": {"price": 187.5e9, "rate": 7500},
    "Ruby Drill": {"price": 85.5e9, "rate": 4500},
    "Diamond Drill": {"price": 27.5e9, "rate": 2750},
    "Crystal Drill": {"price": 9e9, "rate": 1500},
}

# =========================
# HELPERS
# =========================
def parse_number(text):
    text = text.lower().replace(",", "")
    mult = {"k":1e3, "m":1e6, "b":1e9, "t":1e12}
    if text[-1] in mult:
        return float(text[:-1]) * mult[text[-1]]
    return float(text)

def format_number(n):
    for u in ["", "K", "M", "B", "T", "Qa", "Qi"]:
        if n < 1000:
            return f"{n:.2f}{u}"
        n /= 1000
    return f"{n:.2f}Qi"

def progress_bar(p):
    total = 12
    filled = int(p * total)
    return "█"*filled + "░"*(total-filled)

# =========================
# /SELL
# =========================
@bot.tree.command(name="sell")
async def sell(interaction: discord.Interaction, gas: float, price: float, boost: float = 0):

    base = gas * price
    total = base * (1 + boost/100)
    bonus = total - base

    embed = discord.Embed(title="💰 Sell Calculator", color=0xf1c40f)
    embed.add_field(name="⛽ Gas", value=format_number(gas))
    embed.add_field(name="💵 Price", value=f"${price}")
    embed.add_field(name="⚡ Boost", value=f"{boost}%")
    embed.add_field(name="━━━━━━━━━━━━", value=" ", inline=False)
    embed.add_field(name="💰 Total", value=f"**{format_number(total)}**", inline=False)
    embed.add_field(name="📈 Bonus", value=f"+{format_number(bonus)}", inline=False)

    await interaction.response.send_message(embed=embed)

# =========================
# /PRODUCTION
# =========================
@bot.tree.command(name="production")
async def production(interaction: discord.Interaction, rate: float, time: float, unit: str):

    mult = {"s":1, "m":60, "h":3600, "d":86400}
    if unit not in mult:
        await interaction.response.send_message("Use s / m / h / d")
        return

    total = rate * time * mult[unit]

    embed = discord.Embed(title="⛽ Production Calculator", color=0x00d4ff)
    embed.add_field(name="⚡ Rate/sec", value=format_number(rate))
    embed.add_field(name="⏱ Time", value=f"{time} {unit}")
    embed.add_field(name="━━━━━━━━━━━━", value=" ", inline=False)
    embed.add_field(name="📦 Total Gas", value=f"**{format_number(total)}**", inline=False)

    await interaction.response.send_message(embed=embed)

# =========================
# /DRILLS
# =========================
@bot.tree.command(name="drills")
async def drills_cmd(interaction: discord.Interaction):

    embed = discord.Embed(title="🛢️ Oil Empire Drills", color=0xe67e22)

    for name, d in drills.items():
        embed.add_field(
            name=f"⚙️ {name}",
            value=f"💰 `{format_number(d['price'])}` | ⛽ `{format_number(d['rate'])}/s`",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# =========================
# /AFFORD
# =========================
@bot.tree.command(name="afford")
async def afford(interaction: discord.Interaction, drill: str, cash: str, gas_per_sec: float, boost: float, gas_price: float, amount: int):

    if drill not in drills:
        await interaction.response.send_message("Invalid drill")
        return

    d = drills[drill]
    cash_val = parse_number(cash)

    total_cost = d["price"] * amount
    income_sec = gas_per_sec * gas_price * (1 + boost/100)

    can_buy = int(cash_val // d["price"])
    missing = max(0, total_cost - cash_val)

    time_sec = missing / income_sec if income_sec > 0 else 0

    embed = discord.Embed(
        title=f"⚙️ {drill}\nDrill Affordability Analysis",
        color=0xe74c3c
    )

    embed.add_field(name="💰 Cost", value=format_number(d["price"]))
    embed.add_field(name="📦 Amount", value=amount)
    embed.add_field(name="📄 Total", value=format_number(total_cost))
    embed.add_field(name="💵 Cash", value=format_number(cash_val))
    embed.add_field(name="⚡ Gas/sec", value=format_number(gas_per_sec))
    embed.add_field(name="💸 Income/sec", value=format_number(income_sec))
    embed.add_field(name="━━━━━━━━━━━━", value=" ", inline=False)
    embed.add_field(name="✅ Can Buy", value=can_buy)
    embed.add_field(name="📉 Missing", value=format_number(missing))

    if missing > 0:
        embed.add_field(
            name="⏰ Time Needed",
            value=f"{format_number(time_sec)} sec\n{format_number(time_sec/3600)} hrs\n{format_number(time_sec/86400)} days",
            inline=False
        )

    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# /GOAL
# =========================
@bot.tree.command(name="goal")
async def goal(interaction: discord.Interaction, gas_per_sec: float, boost: float, goal: str, current_cash: str):

    goal_val = parse_number(goal)
    current = parse_number(current_cash)

    needed = max(0, goal_val - current)

    income_sec = gas_per_sec * (1 + boost/100)
    income_hr = income_sec * 3600

    percent = current / goal_val if goal_val > 0 else 0

    time_sec = needed / income_sec if income_sec > 0 else 0

    d = int(time_sec // 86400)
    h = int((time_sec % 86400) // 3600)
    m = int((time_sec % 3600) // 60)

    embed = discord.Embed(title="🎯 Cash Goal Calculator", color=0x2ecc71)

    embed.add_field(name="🎯 Goal", value=format_number(goal_val))
    embed.add_field(name="💵 Current", value=format_number(current))
    embed.add_field(name="📦 Still Needed", value=format_number(needed))
    embed.add_field(name="⛽ Rate/sec", value=format_number(gas_per_sec))
    embed.add_field(name="⚡ Boost", value=f"{boost}%")
    embed.add_field(name="💰 Cash/hr", value=format_number(income_hr))

    embed.add_field(
        name="📊 Progress",
        value=f"{progress_bar(percent)} {percent*100:.1f}%"
    )

    embed.add_field(
        name="⏰ Time to Goal",
        value=f"{d}d {h}h {m}m"
    )

    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# /ADDPRIVATE
# =========================
@bot.tree.command(name="addprivate")
async def addprivate(interaction: discord.Interaction, link: str):

    user = interaction.user.name

    if user not in privates:
        privates[user] = []

    privates[user].append(link)
    save_privates(privates)

    await interaction.response.send_message("✅ Added your private server")

# =========================
# /PRIVATES
# =========================
@bot.tree.command(name="privates")
async def privates_cmd(interaction: discord.Interaction):

    embed = discord.Embed(title="🔗 Private Servers", color=0x3498db)

    for user, links in privates.items():
        for i, link in enumerate(links, 1):
            embed.add_field(
                name=f"{user}'s private {i}",
                value=link,
                inline=False
            )

    await interaction.response.send_message(embed=embed)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")

bot.run(os.getenv("DISCORD_TOKEN"))
