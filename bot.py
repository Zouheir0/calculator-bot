import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

OWNER_ID = 985093025887830047

# =========================
# DRILLS (ALL 22)
# =========================
drills = {
    "Basic Drill": (500, 1),
    "Strong Drill": (1800, 3),
    "Enhanced Drill": (3600, 4),
    "Speed Drill": (7200, 6),
    "Reinforced Drill": (12000, 8),
    "Industrial Drill": (20000, 10),
    "Double Industrial Drill": (30000, 12),
    "Turbo Drill": (80000, 16),
    "Mega Drill": (140000, 20),
    "Mega Emerald Drill": (400000, 25),
    "Hell Drill": (1.23e6, 35),
    "Plasma Drill": (4.5e6, 50),
    "Mega Plasma Drill": (95e6, 275),
    "Multi Drill": (280e6, 350),
    "Ice Plasma Drill": (2.4e9, 800),
    "Crystal Drill": (9e9, 1500),
    "Diamond Drill": (27.5e9, 2750),
    "Ruby Drill": (85.5e9, 4500),
    "Fusion Drill": (187.5e9, 7500),
    "Uranium Drill": (437.5e9, 12500),
}

# =========================
# STORAGE
# =========================
privates = {}

# =========================
# HELPERS
# =========================
def parse_number(text: str):
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
    bars = 10
    filled = int(p * bars)
    return "█"*filled + "░"*(bars-filled)

# =========================
# /SELL
# FIX: boost default MUST be float
# =========================
@bot.tree.command(name="sell", description="Calculate money from selling gas")
@app_commands.describe(
    gas="Amount of gas (k/m/b/t)",
    price="Sell price (0-15)",
    boost="Cash boost %"
)
async def sell(
    interaction: discord.Interaction,
    gas: str,
    price: float,
    boost: float = 0.0
):
    gas_val = parse_number(gas)
    total = gas_val * price * (1 + boost/100)
    bonus = total - (gas_val * price)

    embed = discord.Embed(title="💰 Sell Calculator", color=0xffaa00)
    embed.add_field(name="Gas", value=format_number(gas_val))
    embed.add_field(name="Total", value=format_number(total))
    embed.add_field(name="Bonus", value=format_number(bonus))
    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# /PRODUCTION
# =========================
@bot.tree.command(name="production", description="Calculate gas production over time")
@app_commands.describe(
    rate="Gas per second",
    time="Time amount",
    unit="s/m/h/d"
)
async def production(interaction: discord.Interaction, rate: str, time: float, unit: str):

    rate_val = parse_number(rate)

    mult = {"s":1, "m":60, "h":3600, "d":86400}
    if unit not in mult:
        await interaction.response.send_message("Invalid unit (s/m/h/d)")
        return

    total = rate_val * time * mult[unit]

    embed = discord.Embed(title="⛽ Production", color=0x00ffcc)
    embed.add_field(name="Total Gas", value=format_number(total))
    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# DRILL CHOICES
# =========================
drill_choices = [
    app_commands.Choice(name=name, value=name) for name in drills.keys()
]

# =========================
# /DRILLAFFORD
# =========================
@bot.tree.command(name="drillafford", description="Analyze drill affordability")
@app_commands.describe(
    drill="Select drill",
    cash="Current cash",
    gas_per_sec="Gas per second",
    boost="Cash boost %",
    price="Sell price",
    amount="Amount of drills"
)
@app_commands.choices(drill=drill_choices)
async def drillafford(
    interaction: discord.Interaction,
    drill: app_commands.Choice[str],
    cash: str,
    gas_per_sec: str,
    boost: float,
    price: float,
    amount: int
):

    price_d, _ = drills[drill.value]

    cash_val = parse_number(cash)
    gas_val = parse_number(gas_per_sec)

    total_cost = price_d * amount
    income_sec = gas_val * price * (1 + boost/100)

    can_buy = int(cash_val // price_d)
    missing = max(0, total_cost - cash_val)

    time_sec = missing / income_sec if income_sec > 0 else 0

    embed = discord.Embed(
        title=f"⚙️ {drill.value} Drill Analysis",
        color=0xffaa00
    )

    embed.add_field(name="Cost", value=format_number(price_d))
    embed.add_field(name="Amount", value=amount)
    embed.add_field(name="Total", value=format_number(total_cost))
    embed.add_field(name="Cash", value=format_number(cash_val))
    embed.add_field(name="Gas/sec", value=format_number(gas_val))
    embed.add_field(name="Income/sec", value=format_number(income_sec))
    embed.add_field(name="Can Buy", value=can_buy)
    embed.add_field(name="Missing", value=format_number(missing))

    if missing > 0:
        embed.add_field(
            name="Time Needed",
            value=f"{format_number(time_sec)} sec\n{format_number(time_sec/3600)} hrs\n{format_number(time_sec/86400)} days",
            inline=False
        )

    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# PRIVATE SERVERS
# =========================
@bot.tree.command(name="addprivate", description="Add private server link")
async def addprivate(interaction: discord.Interaction, link: str):

    uid = interaction.user.id
    privates.setdefault(uid, []).append(link)

    await interaction.response.send_message("✅ Added")

@bot.tree.command(name="removeprivate", description="Remove private server")
async def removeprivate(interaction: discord.Interaction, index: int):

    uid = interaction.user.id

    if uid not in privates or index < 1 or index > len(privates[uid]):
        await interaction.response.send_message("❌ Invalid index")
        return

    privates[uid].pop(index - 1)
    await interaction.response.send_message("🗑️ Removed")

@bot.tree.command(name="privates", description="Show private servers")
async def privates_cmd(interaction: discord.Interaction):

    embed = discord.Embed(title="🔗 Private Servers", color=0x00ffcc)

    for uid, links in privates.items():
        user = await bot.fetch_user(uid)

        for i, link in enumerate(links, 1):
            embed.add_field(
                name=f"{user.name}'s private {i}",
                value=link,
                inline=False
            )

    embed.set_footer(text="U.E.O")
    await interaction.response.send_message(embed=embed)

# =========================
# /GOAL
# =========================
@bot.tree.command(name="goal", description="Time to reach goal")
async def goal(
    interaction: discord.Interaction,
    gas_per_sec: str,
    boost: float,
    goal: str,
    current_cash: str
):

    gas_val = parse_number(gas_per_sec)
    goal_val = parse_number(goal)
    current = parse_number(current_cash)

    needed = goal_val - current

    income_sec = gas_val * (1 + boost/100)

    percent = current / goal_val if goal_val > 0 else 0
    time_sec = needed / income_sec if income_sec > 0 else 0

    d = int(time_sec // 86400)
    h = int((time_sec % 86400) // 3600)
    m = int((time_sec % 3600) // 60)

    embed = discord.Embed(title="🎯 Goal Calculator", color=0x00ff99)

    embed.add_field(name="Goal", value=format_number(goal_val))
    embed.add_field(name="Current", value=format_number(current))
    embed.add_field(name="Needed", value=format_number(needed))
    embed.add_field(name="Rate/sec", value=format_number(gas_val))
    embed.add_field(name="Boost", value=f"{boost}%")
    embed.add_field(name="Progress", value=f"{progress_bar(percent)} {percent*100:.1f}%")
    embed.add_field(name="Time", value=f"{d}d {h}h {m}m")

    embed.set_footer(text="U.E.O")

    await interaction.response.send_message(embed=embed)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")

bot.run(os.getenv("DISCORD_TOKEN"))
