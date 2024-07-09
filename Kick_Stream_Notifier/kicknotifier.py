from redbot.core import commands, Config
from discord import Embed, TextChannel
import aiohttp

class KickNotifier(commands.Cog):
    """Cog to notify when specified users start streaming on Kick"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_guild = {
            "kick_users": [],
            "notification_channel": None
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def kicknotifier(self, ctx):
        """Commands to manage Kick Notifier"""
        pass

    @kicknotifier.command()
    async def adduser(self, ctx, kick_username: str):
        """Add a Kick user to the notification list"""
        async with self.config.guild(ctx.guild).kick_users() as users:
            if kick_username not in users:
                users.append(kick_username)
                await ctx.send(f"User {kick_username} added to the notification list.")
            else:
                await ctx.send(f"User {kick_username} is already in the notification list.")

    @kicknotifier.command()
    async def removeuser(self, ctx, kick_username: str):
        """Remove a Kick user from the notification list"""
        async with self.config.guild(ctx.guild).kick_users() as users:
            if kick_username in users:
                users.remove(kick_username)
                await ctx.send(f"User {kick_username} removed from the notification list.")
            else:
                await ctx.send(f"User {kick_username} is not in the notification list.")

    @kicknotifier.command()
    async def setchannel(self, ctx, channel: TextChannel):
        """Set the channel for Kick stream notifications"""
        await self.config.guild(ctx.guild).notification_channel.set(channel.id)
        await ctx.send(f"Notification channel set to {channel.mention}")

    @kicknotifier.command()
    async def getchannel(self, ctx):
        """Get the current notification channel"""
        channel_id = await self.config.guild(ctx.guild).notification_channel()
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await ctx.send(f"Current notification channel is {channel.mention}")
            else:
                await ctx.send("The configured notification channel is not accessible.")
        else:
            await ctx.send("No notification channel has been set.")

    @kicknotifier.command()
    async def listusers(self, ctx):
        """List all Kick users in the notification list"""
        users = await self.config.guild(ctx.guild).kick_users()
        if users:
            await ctx.send("Configured Kick streamers:\n" + "\n".join(users))
        else:
            await ctx.send("No Kick streamers have been configured.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Check if users are streaming on Kick when bot is ready"""
        await self.check_kick_streams()

    async def check_kick_streams(self):
        guilds = self.bot.guilds
        for guild in guilds:
            users = await self.config.guild(guild).kick_users()
            for user in users:
                is_live = await self.is_user_live_on_kick(user)
                if is_live:
                    await self.send_notification(guild, user)

    async def is_user_live_on_kick(self, username):
        """Check if the user is live on Kick"""
        url = f"https://api.kick.com/v1/users/{username}/streams"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["live"]
        return False

    async def send_notification(self, guild, username):
        """Send notification that user is live"""
        channel_id = await self.config.guild(guild).notification_channel()
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                embed = Embed(title="Kick Stream Alert", description=f"{username} is now live on Kick!", color=0x1DA1F2)
                embed.add_field(name="Watch here", value=f"https://kick.com/{username}")
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(KickNotifier(bot))
