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
# PARSE NUMBER (K, M, B, T)
# =========================
def parse_number(value: str) -> float:
    value = value.lower().replace(",", "").strip()

    if value.endswith("k"):
        return float(value[:-1]) * 1_000
    elif value.endswith("m"):
        return float(value[:-1]) * 1_000_000
    elif value.endswith("b"):
        return float(value[:-1]) * 1_000_000_000
    elif value.endswith("t"):
        return float(value[:-1]) * 1_000_000_000_000
    else:
        return float(value)


# =========================
# FORMAT NUMBER (UP TO TRILLION)
# =========================
def format_number(num: float) -> str:
    if num >= 1_000_000_000_000:
        return f"{round(num / 1_000_000_000_000, 2)}T"
    elif num >= 1_000_000_000:
        return f"{round(num / 1_000_000_000, 2)}B"
    elif num >= 1_000_000:
        return f"{round(num / 1_000_000, 2)}M"
    elif num >= 1_000:
        return f"{round(num / 1_000, 2)}K"
    else:
        return f"{round(num, 2)}"


# =========================
# SELL COMMAND
# =========================
@bot.tree.command(name="sell", description="Oil Empire sell calculator")
@app_commands.describe(
    price="Price per unit (example: 10)",
    amount="Oil amount (example: 62.8M)",
    boost="Cash boost % (example: 160)"
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
        embed.add_field(name="Bonus Earned", value=f"+${format_number(bonus)}", inline=True)
        embed.add_field(name="Total Profit", value=f"💰 ${format_number(total)}", inline=False)

        await interaction.response.send_message(embed=embed)

    except:
        await interaction.response.send_message("❌ Invalid input. Example: /sell price:10 amount:62.8M boost:160")


# =========================
# PRODUCTION COMMAND
# =========================
@bot.tree.command(name="production", description="Calculate oil production over time")
@app_commands.describe(
    rate="Oil per second (example: 10K)",
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

        # Determine which time was used
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
            title="⛽ Oil Production Calculator",
            color=discord.Color.blue()
        )

        embed.add_field(name="Production Rate", value=f"{format_number(rate_val)}/s", inline=False)
        embed.add_field(name="Time", value=f"{time_value} {unit}", inline=True)
        embed.add_field(name="Total Oil", value=f"🛢️ {format_number(total)}", inline=False)

        await interaction.response.send_message(embed=embed)

    except:
        await interaction.response.send_message("❌ Invalid input. Example: /production rate:10K hours:5")


# =========================
# RUN BOT
# =========================
bot.run(os.getenv("DISCORD_TOKEN"))
