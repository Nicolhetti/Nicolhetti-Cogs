from .kickstreameralert import KickStreamerAlert

def setup(bot):
    bot.add_cog(KickStreamerAlert(bot))
