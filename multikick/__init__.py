from .multikick import MultiKick

async def setup(bot):
    cog = MultiKick(bot)
    bot.add_cog(cog)
