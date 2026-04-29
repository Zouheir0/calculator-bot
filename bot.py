import discord
from discord import app_commands
from discord.ext import commands
import os
import math

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


# =========================
# PARSE NUMBER (K, M, B)
# =========================
def parse_number(value: str) -> float:
    value = value.lower().replace(",", "").strip()

    if value.endswith("k"):
        return float(value[:-1]) * 1_000
    elif value.endswith("m"):
        return float(value[:-1]) * 1_000_000
    elif value.endswith("b"):
        return float(value[:-1]) * 1_000_000_000
    else:
        return float(value)


# =========================
# FORMAT NUMBER (GAME STYLE)
# =========================
def format_number(num: float) -> str:
    # mimic Roblox-style rounding (1 decimal usually)
    if num >= 1_000_000_000:
        return f"{round(num / 1_000_000_000, 1)}B"
    elif num >= 1_000_000:
        return f"{round(num / 1_000_000, 1)}M"
    elif num >= 1_000:
        return f"{round(num / 1_000, 1)}K"
    else:
        return f"{round(num, 1)}"


# =========================
# SELL CALCULATOR (GAME ACCURATE)
# =========================
@bot.tree.command(name="sell", description="Oil Empire sell calculator")
@app_commands.describe(
    price="Price per unit (example: 10)",
    amount="Oil amount (example: 62.8M)",
    boost="Cash boost % (example: 160)"
)
async def sell(
    interaction: discord.Interaction,
    price: str,
    amount: str,
    boost: float
):
    try:
        price_val = parse_number(price)
        amount_val = parse_number(amount)

        # base money
        base = price_val * amount_val

        # GAME FORMULA (confirmed)
        total = base * (boost / 100.0)

        # simulate in-game rounding (important)
        total = round(total, 1)
        base = round(base, 1)

        bonus = total - base

        await interaction.response.send_message(
            f"🛢️ **Sell Calculator (Oil Empire Accurate)**\n"
            f"Base: `{format_number(base)}$`\n"
            f"Boost: `{boost}%`\n"
            f"Bonus: `+{format_number(bonus)}$`\n"
            f"Total: `{format_number(total)}$`"
        )

    except:
        await interaction.response.send_message("❌ Invalid input. Example: /sell price:10 amount:62.8M boost:160")


# =========================
# PRODUCTION CALCULATOR
# =========================
@bot.tree.command(name="production", description="Calculate oil production over time")
@app_commands.describe(
    rate="Oil per second (example: 10K)",
    seconds="Seconds (optional)",
    hours="Hours (optional)",
    days="Days (optional)"
)
async def production(
    interaction: discord.Interaction,
    rate: str,
    seconds: float = 0.0,
    hours: float = 0.0,
    days: float = 0.0
):
    try:
        rate_val = parse_number(rate)

        total_seconds = seconds + (hours * 3600.0) + (days * 86400.0)

        total = rate_val * total_seconds

        # round like game
        total = round(total, 1)

        await interaction.response.send_message(
            f"⛽ **Production Calculator**\n"
            f"Rate: `{format_number(rate_val)}/s`\n"
            f"Time: `{int(total_seconds)} seconds`\n"
            f"Total Oil: `{format_number(total)}`"
        )

    except:
        await interaction.response.send_message("❌ Invalid input. Example: /production rate:10K hours:5")


# =========================
# RUN BOT
# =========================
bot.run(os.getenv("DISCORD_TOKEN"))
