import picbot
import pytest
import os


@pytest.fixture()
def bot():
    token = os.environ.get('TOKEN')
    if not token.startswith('xoxb-'):
        return "token not defined."
    return picbot.bot.PictBot(token)


@pytest.mark.asyncio
async def test_picbot_joke(bot):
    bot.jokes = ['Tire mon doigt']
    assert 'Tire mon doigt' == await bot.joke()

@pytest.mark.asyncio
async def test_picbot_help(bot):
    assert "Welcome to our Picture bot ! \n" \
                      "This bot is here to send you some funny pictures from some funny websites. \n" \
                      "Here are the commands : \n" \
                      " - pic : uploads a picture. \n" \
                      " - picture : one and the same. =P \n" \
                      " - joke : gets you a random joke for you, programmer. \n" \
                      " - help : You already know this one, don't you. \n" \
                      "Have fun !" == await bot.help()


@pytest.mark.asyncio
async def test_picbot_error(bot):
    assert "Command not found. Type 'help' for a list of valid commands." == await bot.error()


@pytest.mark.asyncio
async def test_picbot_pic(bot):
    link = await bot.picture()
    assert link.startswith("http://imgs.xkcd.com/comics/")
