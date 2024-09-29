from redbot.core import commands, Config
from redbot.core.bot import Red
from discord.ext import tasks
import discord
from datetime import datetime, timedelta

class MultiKick(commands.Cog):
    """Expulsa a múltiples usuarios del servidor y usuarios inactivos si está activado."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1333381216, force_registration=True)
        
        default_guild = {
            "auto_kick_inactive": False,
            "inactive_days": 30,
            "kick_reason": "Inactividad prolongada",
        }
        
        self.config.register_guild(**default_guild)
        self.check_inactive_users.start()

    def cog_unload(self):
        self.check_inactive_users.cancel()

    @commands.command()
    @commands.guild_only()
    @commands.admin_or_permissions(kick_members=True)
    async def multikick(self, ctx, *users: discord.Member, reason: str = None):
        """Expulsa a múltiples usuarios del servidor.
        
        Uso: [p]multikick @user1 @user2 @user3 ... razón
        """
        if not users:
            await ctx.send("Por favor menciona a los usuarios que deseas expulsar.")
            return
        
        failed_kicks = []
        for user in users:
            try:
                await ctx.guild.kick(user, reason=reason)
                await ctx.send(f"{user.name} ha sido expulsado por la razón: {reason}")
            except Exception as e:
                failed_kicks.append(f"{user.name} (Error: {e})")
        
        if failed_kicks:
            await ctx.send(f"No se pudo expulsar a los siguientes usuarios: {', '.join(failed_kicks)}")

    @commands.group()
    @commands.guild_only()
    @commands.admin_or_permissions(kick_members=True)
    async def inactivekick(self, ctx):
        """Comandos para configurar la expulsión automática de usuarios inactivos."""
        pass

    @inactivekick.command()
    async def toggle(self, ctx, state: bool):
        """Activa o desactiva la expulsión automática de usuarios inactivos."""
        await self.config.guild(ctx.guild).auto_kick_inactive.set(state)
        status = "activada" if state else "desactivada"
        await ctx.send(f"La expulsión automática de usuarios inactivos ha sido {status}.")

    @inactivekick.command()
    async def setdays(self, ctx, days: int):
        """Configura el número de días de inactividad antes de expulsar."""
        await self.config.guild(ctx.guild).inactive_days.set(days)
        await ctx.send(f"El número de días de inactividad ha sido establecido en {days} días.")

    @inactivekick.command()
    async def reason(self, ctx, *, reason: str):
        """Configura la razón de la expulsión de usuarios inactivos."""
        await self.config.guild(ctx.guild).kick_reason.set(reason)
        await ctx.send(f"La razón para la expulsión de inactivos ha sido cambiada a: {reason}")

    @tasks.loop(hours=24)
    async def check_inactive_users(self):
        """Verifica y expulsa a los usuarios inactivos si la función está activada."""
        for guild in self.bot.guilds:
            auto_kick = await self.config.guild(guild).auto_kick_inactive()
            if not auto_kick:
                continue
            
            inactive_days = await self.config.guild(guild).inactive_days()
            reason = await self.config.guild(guild).kick_reason()
            threshold_date = datetime.utcnow() - timedelta(days=inactive_days)
            
            for member in guild.members:
                if member.bot or member.guild_permissions.administrator:
                    continue  # No expulsar bots o administradores
                
                last_message = await self.get_last_message_date(member)
                if last_message is None or last_message < threshold_date:
                    try:
                        await guild.kick(member, reason=reason)
                        channel = guild.system_channel or guild.text_channels[0]
                        if channel:
                            await channel.send(f"{member.name} ha sido expulsado por inactividad ({inactive_days} días).")
                    except Exception as e:
                        print(f"Error expulsando a {member.name}: {e}")

    async def get_last_message_date(self, member):
        """Obtiene la fecha del último mensaje de un miembro."""
        async for message in member.guild.history(limit=100, oldest_first=False):
            if message.author == member:
                return message.created_at
        return None

    @check_inactive_users.before_loop
    async def before_check_inactive_users(self):
        await self.bot.wait_until_ready()
