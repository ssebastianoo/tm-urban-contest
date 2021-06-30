from discord.ext import tasks
import asyncio

@tasks.loop(seconds=5)
async def my_loop():
    f = open("oof.txt", "w")
    f.write("oof")
    f.close()

my_loop.start()
