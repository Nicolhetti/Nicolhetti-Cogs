from redbot.core import commands
from redbot.core.bot import Red

class AutoBan(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Verifica si el autor del mensaje no es un bot
        if message.author.bot:
            return

        # Verifica si el mensaje contiene @everyone o @here
        if "@everyone" in message.content or "@here" in message.content:
            # Obtiene el servidor (guild) y el autor del mensaje
            guild = message.guild
            member = message.author

            # Banea al miembro
            await guild.ban(member, reason="Uso no autorizado de @everyone o @here")

            # Envía un mensaje en el canal donde se detectó la mención
            await message.channel.send(f'{member.mention} ha sido baneado por usar @everyone o @here.')
