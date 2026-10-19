import discord
from discord.ext import commands
from discord import ui
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- VISTA DEL TICKET ---
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🎫 Apri Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Controlla se ha già un ticket
        existing = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message(f"Hai già un ticket aperto: {existing.mention}", ephemeral=True)
            return

        # Crea canale
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        # Se c'è un ruolo Staff, dagli accesso
        staff_role = discord.utils.get(guild.roles, name="Staff")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites, reason=f"Ticket di {user}")
        
        embed = discord.Embed(title="Ticket Aperto", description=f"Ciao {user.mention}, lo staff ti risponderà a breve.\nClicca 🔒 per chiudere.", color=0x00ff00)
        await channel.send(content=f"{user.mention} {staff_role.mention if staff_role else ''}", embed=embed, view=CloseView())
        await interaction.response.send_message(f"Ticket creato: {channel.mention}", ephemeral=True)

class CloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Chiudo il ticket in 3 secondi...", ephemeral=True)
        await interaction.channel.delete(reason="Ticket chiuso")

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizzati {len(synced)} comandi")
    except Exception as e:
        print(e)

@bot.tree.command(name="ticket", description="Manda il pannello ticket")
@commands.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(title="Supporto", description="Hai bisogno di aiuto? Clicca il bottone qui sotto per aprire un ticket privato con lo Staff.", color=0x5865f2)
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Pannello inviato!", ephemeral=True)

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)