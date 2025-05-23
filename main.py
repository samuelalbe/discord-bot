import discord
from discord.ext import commands, tasks
from discord import app_commands
from collections import defaultdict
import datetime

# ===== INTENTI =====
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

# ===== BOT =====
class StatBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.stats = {
            "joins": defaultdict(int),
            "messages": defaultdict(int),
            "bans": defaultdict(int),
            "mutes": defaultdict(int)
        }

    async def setup_hook(self):
        await self.tree.sync()
        daily_report.start()

bot = StatBot()

# ===== FUNZIONE DATA =====
def get_date_key():
    now = datetime.datetime.utcnow()
    return now.strftime("%Y-%m-%d")

# ===== EVENTI =====
@bot.event
async def on_ready():
    print(f"✅ Bot avviato come {bot.user}")

@bot.event
async def on_member_join(member):
    date_key = get_date_key()
    bot.stats["joins"][date_key] += 1

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    date_key = get_date_key()
    bot.stats["messages"][date_key] += 1
    await bot.process_commands(message)

@bot.event
async def on_member_ban(guild, user):
    date_key = get_date_key()
    bot.stats["bans"][date_key] += 1

# ===== COMANDO !addmute =====
@bot.command()
@commands.has_permissions(administrator=True)
async def addmute(ctx, member: discord.Member):
    date_key = get_date_key()
    bot.stats["mutes"][date_key] += 1
    await ctx.send(f"{member.mention} è stato registrato come 'mutato'.")

# ===== COMANDO SLASH /statistiche =====
@bot.tree.command(name="statistiche", description="Mostra le statistiche di oggi")
async def slash_statistiche(interaction: discord.Interaction):
    today = get_date_key()
    stats = bot.stats
    joins = stats["joins"].get(today, 0)
    messages = stats["messages"].get(today, 0)
    bans = stats["bans"].get(today, 0)
    mutes = stats["mutes"].get(today, 0)

    embed = discord.Embed(title=f"📊 Statistiche di oggi ({today})", color=discord.Color.green())
    embed.add_field(name="👥 Join", value=str(joins), inline=False)
    embed.add_field(name="💬 Messaggi", value=str(messages), inline=False)
    embed.add_field(name="🔇 Mutes", value=str(mutes), inline=False)
    embed.add_field(name="⛔ Bans", value=str(bans), inline=False)
    embed.set_footer(text="Bot Statistiche")

    await interaction.response.send_message(embed=embed)

# ===== REPORT GIORNALIERO =====
@tasks.loop(hours=24)
async def daily_report():
    await bot.wait_until_ready()
    channel = discord.utils.get(bot.get_all_channels(), name="statistiche")
    if not channel:
        print("⚠️ Canale 'statistiche' non trovato.")
        return

    today = get_date_key()
    joins = bot.stats["joins"].get(today, 0)
    messages = bot.stats["messages"].get(today, 0)
    bans = bot.stats["bans"].get(today, 0)
    mutes = bot.stats["mutes"].get(today, 0)

    embed = discord.Embed(title=f"📊 Statistiche del giorno: {today}", color=discord.Color.blue())
    embed.add_field(name="👥 Nuovi membri", value=str(joins), inline=False)
    embed.add_field(name="💬 Messaggi scritti", value=str(messages), inline=False)
    embed.add_field(name="🔇 Mute registrati", value=str(mutes), inline=False)
    embed.add_field(name="🔨 Ban effettuati", value=str(bans), inline=False)
    embed.set_footer(text="Bot Statistiche")

    await channel.send(embed=embed)

# ===== AVVIO BOT =====
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


