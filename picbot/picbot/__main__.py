import asyncio
import os

from . import bot

if __name__ == "__main__":
    token = os.environ.get('TOKEN')
    loop = asyncio.get_event_loop()
    my_bot = bot.PictBot(token)
    loop.run_until_complete(my_bot.connect())
    loop.close()
