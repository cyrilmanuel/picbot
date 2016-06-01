import picbot
import pytest

@pytest.fixture()
def bot():
    return picbot.PictBot()

def test_picbot(bot):
    bot.jokes = ['Tire mon doigt']
    assert 'Tire mon doigt' == bot.joke()
