import discord
from redbot.core import commands, Config, checks
import aiohttp
import asyncio

class KickStreamerAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_guild(
            streamers=[],
            alert_channel=None,
            alert_message="{streamer} está en directo en Kick! {url}",
            update_interval=60
        )
        self.session = aiohttp.ClientSession()
        self.task = self.bot.loop.create_task(self.check_streamers())

    @commands.group()
    async def kickalert(self, ctx):
        """Comandos para configurar las alertas de streamers en Kick"""
        pass

    @kickalert.command()
    @checks.admin()
    async def add(self, ctx, streamer: str):
        """Agrega un streamer a la lista de alertas"""
        async with self.config.guild(ctx.guild).streamers() as streamers:
            if streamer not in streamers:
                streamers.append(streamer)
                await ctx.send(f"{streamer} ha sido agregado a la lista de alertas.")
            else:
                await ctx.send(f"{streamer} ya está en la lista de alertas.")

    @kickalert.command()
    @checks.admin()
    async def remove(self, ctx, streamer: str):
        """Elimina un streamer de la lista de alertas"""
        async with self.config.guild(ctx.guild).streamers() as streamers:
            if streamer in streamers:
                streamers.remove(streamer)
                await ctx.send(f"{streamer} ha sido eliminado de la lista de alertas.")
            else:
                await ctx.send(f"{streamer} no está en la lista de alertas.")

    @kickalert.command()
    async def list(self, ctx):
        """Muestra la lista de streamers configurados"""
        streamers = await self.config.guild(ctx.guild).streamers()
        if streamers:
            await ctx.send(f"Streamers configurados: {', '.join(streamers)}")
        else:
            await ctx.send("No hay streamers configurados.")

    @kickalert.command()
    @checks.admin()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Configura el canal donde se enviarán las alertas"""
        await self.config.guild(ctx.guild).alert_channel.set(channel.id)
        await ctx.send(f"Canal de alertas configurado a {channel.mention}")

    @kickalert.command()
    @checks.admin()
    async def setmessage(self, ctx, *, message: str):
        """Configura el mensaje de alerta"""
        await self.config.guild(ctx.guild).alert_message.set(message)
        await ctx.send("Mensaje de alerta configurado.")

    @kickalert.command()
    @checks.admin()
    async def setinterval(self, ctx, interval: int):
        """Configura el intervalo de actualización en segundos"""
        await self.config.guild(ctx.guild).update_interval.set(interval)
        await ctx.send(f"Intervalo de actualización configurado a {interval} segundos.")

    @kickalert.command()
    async def testalert(self, ctx):
        """Prueba la alerta de streamers"""
        alert_channel_id = await self.config.guild(ctx.guild).alert_channel()
        alert_channel = self.bot.get_channel(alert_channel_id)
        if alert_channel:
            alert_message = await self.config.guild(ctx.guild).alert_message()
            await alert_channel.send(alert_message.format(streamer="TestStreamer", url="https://kick.com/TestStreamer"))
            await ctx.send("Alerta de prueba enviada.")
        else:
            await ctx.send("Canal de alertas no configurado.")

    async def check_streamers(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            all_guilds = await self.config.all_guilds()
            for guild_id, guild_data in all_guilds.items():
                streamers = guild_data.get("streamers", [])
                alert_channel_id = guild_data.get("alert_channel")
                alert_message = guild_data.get("alert_message", "{streamer} está en directo en Kick! {url}")
                update_interval = guild_data.get("update_interval", 60)
                if streamers and alert_channel_id:
                    alert_channel = self.bot.get_channel(alert_channel_id)
                    if alert_channel:
                        for streamer in streamers:
                            if await self.is_live(streamer):
                                await alert_channel.send(alert_message.format(streamer=streamer, url=f"https://kick.com/{streamer}"))
                await asyncio.sleep(update_interval)

    async def is_live(self, streamer: str):
        url = f"https://kick.com/api/v1/channels/{streamer}"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("live", False)
        return False

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        self.task.cancel()

def setup(bot):
    bot.add_cog(KickStreamerAlert(bot))


# I'm very sorry if something doesn't work well, I'm very new to programming and I use AI to help me :(.
# Lo siento mucho si algo no funciona bien, soy muy nuevo en programación y uso IA para ayudarme :(.
