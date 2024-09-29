from .multikick import MultiKick

async def setup(bot):
    cog = MultiKick(bot)
    await bot.add_cog(cog)
