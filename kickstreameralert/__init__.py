from .kickstreameralert import KickStreamerAlert

async def setup(bot):
    await bot.add_cog(KickStreamerAlert(bot))
