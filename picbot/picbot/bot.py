"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp
import random
import xkcd
# import antigravity # CAREFUL : Dangerous ! Velociraptors might appear.

from .api import api_call
from config import DEBUG, TOKEN

# Le bot :
#   -Ne répond que lorsqu'on s'addresse à lui, sous forme de texte.
#   -Répond aux commandes pic, picture, joke et help.
#   -Dirige les utilisateurs vers la commande help si aucune bonne commande entrée.


class PictBot:
    """This object is able to connect to Slack and to send jokes and random images from XKCD."""
    def __init__(self, token=TOKEN):
        self.token = token
        self.rtm = None
        self.api = {
            "pic": self.picture,
            "picture": self.picture,
            "joke": self.joke,
            "help": self.help,
        }

        self.jokes = [
            "Knock, Knock \n - Who's there? \n - Your Java Update",
            "Knock, Knock \n - Who's there? \n *Long Pause* \n - Java",
            "A SQL query goes into a bar, walks up to two tables and asks, 'Can I join you?'",
            "When your hammer is C++, everything begins to look like a thumb.",
            "programmer (noun) An organism capable of converting caffeine into code."
        ]

    async def sendText(self, message, channel_id, user_name, team_id):
        """Sends a text message to the channel.

        :param message: the text message to sens to the channel.
        :param channel_id: id of the channel to send the message to.
        :param user_name: name of the user you would like to adress.
        :param team_id: id of the team your bot is in.
        :returns: answer from the api_call."""
        return await api_call('chat.postMessage', {"type": "message",
                                                   "channel": channel_id,
                                                   "text": "<@{0}> {1}".format(user_name["user"]["name"], message),
                                                   "team": team_id})

    async def joke(self):
        """Select randomly a joke from the list.

        :returns: text chosen by the method."""
        return random.choice(self.jokes)

    async def picture(self):
        """Sends a picture to the channel

        :returns: URL of the image chosen by the method."""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, xkcd.getRandomComic)  # Permet une réelle parallelisation
        comic = await future
        return comic.getImageLink()

    async def help(self):
        """Displays the help message to the channel

        :returns: help text."""
        return "Welcome to our Picture bot ! \n" \
                      "This bot is here to send you some funny pictures from some funny websites. \n" \
                      "Here are the commands : \n" \
                      " - pic : uploads a picture. \n" \
                      " - picture : one and the same. =P \n" \
                      " - joke : gets you a random joke for you, programmer. \n" \
                      " - help : You already know this one, don't you. \n" \
                      "Have fun !"

    async def error(self):
        """displays the error message to the channel, in case of bad input.

        :returns: error text."""
        return "Command not found. Type 'help' for a list of valid commands."

    async def process(self, message):
        """Processes input messages.

        :param message: brute message coming from Slack, waiting to be processed."""

        if message.get('type') == 'message':
            # _____________________________________________
            # _____________________________________________
            # ///////////INFORMATION FORMATTING\\\\\\\\\\\\
            # _____________________________________________
            # _____________________________________________

            # Channel-related entries
            # Un-comment this next line if your bot should be active in all channels he's invited in
            channel_id = message.get('channel')

            # Team-related entries
            team_id = self.rtm['team']['id']  # gets id of the active team

            # User-related entries
            user_id = message.get('user')
            user_name = await api_call('users.info',  # gets user name based on id
                                       {'user': user_id})

            # Self-related entries
            bot_id = self.rtm['self']['id']  # gets id of self, meaning the bot.
            # message related entries
            message_text = message.get('text')

            # _____________________________________________
            # _____________________________________________
            # ///////////ANSWER DECISION MAKING\\\\\\\\\\\\
            # _____________________________________________
            # _____________________________________________

            # Splits message in half, with recipient on the left side, and the core text on the other.
            if (isinstance(message_text, str)):
                message_split = message_text.split(':', 1)  # Generate an exception if type is different than text.
                recipient = message_split[0].strip()

                if len(message_split) > 0 and recipient == '<@{0}>'.format(bot_id):  # If message is adressed to our bot
                    core_text = message_split[1].strip()
                    action = self.api.get(core_text) or self.error
                    response_text = await action()
                    print(await self.sendText(response_text, channel_id, user_name, team_id))

    async def connect(self):
        """Connects the bot to Slack"""

        self.rtm = await api_call('rtm.start')
        assert self.rtm['ok'], self.rtm['error']

        with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.rtm["url"]) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.MsgType.text
                    message = json.loads(msg.data)
                    asyncio.ensure_future(self.process(message))


