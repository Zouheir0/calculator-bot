import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# BOT READY EVENT
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
# COMMAND 1: SELL CALCULATOR
# =========================
@bot.tree.command(name="sell", description="Calculate oil selling profit")
@app_commands.describe(
    price="Price per unit of oil",
    amount="Amount of oil you have",
    boost="Cash boost percentage (optional, e.g. 160 for 160%)"
)
async def sell(interaction: discord.Interaction, price: float, amount: float, boost: float = 0):
    base = price * amount

    multiplier = 1 + (boost / 100)
    total = base * multiplier
    extra = total - base

    await interaction.response.send_message(
        f"🛢️ **Oil Sell Calculator**\n"
        f"Base: `{base:,.2f}$`\n"
        f"Boost: `{boost}%`\n"
        f"Bonus: `+{extra:,.2f}$`\n"
        f"Total: `{total:,.2f}$`"
    )


# =========================
# COMMAND 2: PRODUCTION CALCULATOR
# =========================
@bot.tree.command(name="production", description="Calculate oil production over time")
@app_commands.describe(
    rate_per_second="Oil per second production",
    seconds="Seconds (optional)",
    hours="Hours (optional)",
    days="Days (optional)"
)
async def production(
    interaction: discord.Interaction,
    rate_per_second: float,
    seconds: float = 0,
    hours: float = 0,
    days: float = 0
):
    total_seconds = seconds + (hours * 3600) + (days * 86400)

    total = rate_per_second * total_seconds

    await interaction.response.send_message(
        f"⛽ **Production Calculator**\n"
        f"Rate: `{rate_per_second}/s`\n"
        f"Time: `{total_seconds} seconds`\n"
        f"Total Oil: `{total:,.2f}`"
    )


# =========================
# RUN BOT
# =========================
import os
bot.run(os.getenv("MTQ5ODczMzAzMjQ2NTQ5ODE0Mg.G-iNP1.m0xMA13MTOK7Hq_zx3-ObQy76TUVrqkMLluY7Q"))