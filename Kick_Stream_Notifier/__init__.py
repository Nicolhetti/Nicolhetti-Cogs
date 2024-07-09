from .kicknotifier import KickNotifier

def setup(bot):
    bot.add_cog(KickNotifier(bot))
