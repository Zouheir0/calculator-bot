import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("Commands synced")
    except Exception as e:
        print(e)


# =========================
# NUMBER SCALE SYSTEM
# =========================
suffixes = [
    "", "K", "M", "B", "T",
    "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc"
]


# =========================
# PARSE NUMBER
# =========================
def parse_number(value: str) -> float:
    value = value.lower().replace(",", "").strip()

    multipliers = {
        "k": 1e3,
        "m": 1e6,
        "b": 1e9,
        "t": 1e12,
        "qa": 1e15,
        "qi": 1e18,
        "sx": 1e21,
        "sp": 1e24,
        "oc": 1e27,
        "no": 1e30,
        "dc": 1e33
    }

    for suffix, mult in multipliers.items():
        if value.endswith(suffix):
            return float(value[:-len(suffix)]) * mult

    return float(value)


# =========================
# FORMAT NUMBER (ADVANCED)
# =========================
def format_number(num: float) -> str:
    if num == 0:
        return "0"

    index = 0
    while num >= 1000 and index < len(suffixes) - 1:
        num /= 1000
        index += 1

    return f"{round(num, 2)}{suffixes[index]}"


# =========================
# SELL COMMAND
# =========================
@bot.tree.command(name="sell", description="Oil Empire sell calculator")
@app_commands.describe(
    price="Price per unit",
    amount="Oil amount (e.g. 62.8M)",
    boost="Cash boost %"
)
async def sell(interaction: discord.Interaction, price: str, amount: str, boost: float):
    try:
        price_val = parse_number(price)
        amount_val = parse_number(amount)

        base = price_val * amount_val
        total = base * (boost / 100.0)
        bonus = total - base

        embed = discord.Embed(
            title="🛢️ Oil Sell Calculator",
            color=discord.Color.green()
        )

        embed.add_field(name="Base Value", value=f"${format_number(base)}", inline=False)
        embed.add_field(name="Cash Boost", value=f"{boost}%", inline=True)
        embed.add_field(name="Bonus", value=f"+${format_number(bonus)}", inline=True)
        embed.add_field(name="Total", value=f"💰 ${format_number(total)}", inline=False)

        await interaction.response.send_message(embed=embed)

    except:
        await interaction.response.send_message("❌ Invalid input")


# =========================
# PRODUCTION COMMAND
# =========================
@bot.tree.command(name="production", description="Oil production calculator")
@app_commands.describe(
    rate="Oil per second (e.g. 10K)",
    seconds="Seconds",
    minutes="Minutes",
    hours="Hours",
    days="Days"
)
async def production(
    interaction: discord.Interaction,
    rate: str,
    seconds: float = 0.0,
    minutes: float = 0.0,
    hours: float = 0.0,
    days: float = 0.0
):
    try:
        rate_val = parse_number(rate)

        if days > 0:
            time_value = days
            unit = "day(s)"
            total_seconds = days * 86400
        elif hours > 0:
            time_value = hours
            unit = "hour(s)"
            total_seconds = hours * 3600
        elif minutes > 0:
            time_value = minutes
            unit = "minute(s)"
            total_seconds = minutes * 60
        else:
            time_value = seconds
            unit = "second(s)"
            total_seconds = seconds

        total = rate_val * total_seconds

        embed = discord.Embed(
            title="⛽ Oil Production",
            color=discord.Color.blue()
        )

        embed.add_field(name="Rate", value=f"{format_number(rate_val)}/s", inline=False)
        embed.add_field(name="Time", value=f"{time_value} {unit}", inline=True)
        embed.add_field(name="Total Oil", value=f"🛢️ {format_number(total)}", inline=False)

        await interaction.response.send_message(embed=embed)

    except:
        await interaction.response.send_message("❌ Invalid input")


# =========================
# RUN BOT
# =========================
bot.run(os.getenv("DISCORD_TOKEN"))
