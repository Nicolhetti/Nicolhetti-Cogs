from .kickstreameralert import KickStreamerAlert

async def setup(bot):
    bot.add_cog(KickStreamerAlert(bot))
