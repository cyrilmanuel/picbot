import picbot
import pytest

@pytest.fixture()
def bot():
    return picbot.bot.PictBot()


def test_picbot_joke(bot):
    bot.jokes = ['Tire mon doigt']
    assert 'Tire mon doigt' == bot.joke()


def test_picbot_help(bot):
    assert "Welcome to our Picture bot ! \n" \
                      "This bot is here to send you some funny pictures from some funny websites. \n" \
                      "Here are the commands : \n" \
                      " - pic : uploads a picture. \n" \
                      " - picture : one and the same. =P \n" \
                      " - joke : gets you a random joke for you, programmer. \n" \
                      " - help : You already know this one, don't you. \n" \
                      "Have fun !" == bot.help()


def test_picbot_error(bot):
    assert "Command not found. Type 'help' for a list of valid commands." == bot.error()


def test_picbot_pic(bot):
    assert bot.picture().startswith("http://imgs.xkcd.com/comics/")
