from .kicknotifier import KickNotifier

async def setup(bot):
    await bot.add_cog(KickNotifier(bot))
