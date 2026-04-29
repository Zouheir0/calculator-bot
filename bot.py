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
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


# =========================
# HELPER: PARSE NUMBERS (M, B, K)
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
# HELPER: FORMAT NUMBERS
# =========================
def format_number(num: float) -> str:
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.2f}"


# =========================
# COMMAND 1: SELL
# =========================
@bot.tree.command(name="sell", description="Calculate oil selling profit")
@app_commands.describe(
    price="Price per unit (example: 5)",
    amount="Oil amount (example: 34.5M)",
    boost="Cash boost % (optional, example: 160)"
)
async def sell(
    interaction: discord.Interaction,
    price: str,
    amount: str,
    boost: float = 0.0
):
    try:
        price_val = parse_number(price)
        amount_val = parse_number(amount)

        base = price_val * amount_val
        multiplier = 1 + (boost / 100.0)

        total = base * multiplier
        extra = total - base

        await interaction.response.send_message(
            f"🛢️ **Sell Calculator**\n"
            f"Base: `{format_number(base)}$`\n"
            f"Boost: `{boost}%`\n"
            f"Bonus: `+{format_number(extra)}$`\n"
            f"Total: `{format_number(total)}$`"
        )

    except Exception:
        await interaction.response.send_message("❌ Invalid input. Example: price=5 amount=34.5M boost=160")


# =========================
# COMMAND 2: PRODUCTION
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

        await interaction.response.send_message(
            f"⛽ **Production Calculator**\n"
            f"Rate: `{format_number(rate_val)}/s`\n"
            f"Time: `{total_seconds:,.0f} seconds`\n"
            f"Total Oil: `{format_number(total)}`"
        )

    except Exception:
        await interaction.response.send_message("❌ Invalid input. Example: rate=10K hours=5")


# =========================
# RUN BOT
# =========================
bot.run(os.getenv("DISCORD_TOKEN"))
