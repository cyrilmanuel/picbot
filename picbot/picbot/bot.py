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

# Liens utiles :
#   -Méthodes disponibles pour api_call : https://api.slack.com/methods
#   -Guide du prof : https://medium.com/@greut/a-slack-bot-with-pythons-3-5-asyncio-ad766d8b5d8f#.7okn8gngi
#   -rtm documentation : https://api.slack.com/rtm
#   -rtm.start documentation : https://api.slack.com/methods/rtm.start

# Notes :
#   -Le bot n'uplload pas d'images, il va les chercher déjà existantes sur Internet.
#    La méthode file.upload permet de mettre une image en ligne sur les serveurs Slack.
#    Pour l'afficher, il faut ensuite aller chercher son URL, présent dans le texte retourné par la méthode file.upload.

class PictBot:
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
        """Sends a text message to the channel"""
        return await api_call('chat.postMessage', {"type": "message",
                                                   "channel": channel_id,
                                                   "text": "<@{0}> {1}".format(user_name["user"]["name"], message),
                                                   "team": team_id})

    def joke(self):
        """Select randomly a joke from the list."""
        return random.choice(self.jokes)

    async def picture(self, channel_id, user_name, team_id):
        """Sends a picture to the channel"""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, xkcd.getRandomComic)  # Permet une réelle parallelisation
        comic = await future
        link = comic.getImageLink()
        return await self.sendText(link, channel_id, user_name, team_id)

    async def help(self, channel_id, user_name, team_id):
        """Displays the help message to the channel"""
        helpMessage = "Welcome to our Picture bot ! \n" \
                      "This bot is here to send you some funny pictures from some funny websites. \n" \
                      "Here are the commands : \n" \
                      " - pic : uploads a picture. \n" \
                      " - picture : one and the same. =P \n" \
                      " - joke : gets you a random joke for you, programmer. \n" \
                      " - help : You already know this one, don't you. \n" \
                      "Have fun !"
        return await self.sendText(helpMessage, channel_id, user_name, team_id)

    async def error(self, channel_id, user_name, team_id):
        """displays the error message to the channel, in case of bad input"""
        error = "Command not found. Type 'help' for a list of valid commands."
        return await self.sendText(error, channel_id, user_name, team_id)

    async def process(self, message):
        """Processes input messages."""
        # Comment the line below if you want your bot to be active on all channels
        # and don't forget to modify the if statement below too
        # channel_id = 'G1AN77A0L'  # name of the channel you want the bot active in.

        if message.get('type') == 'message':  # and message.get('channel') == channel_id:
            # _____________________________________________
            # _____________________________________________
            # ///////////INFORMATION FORMATTING\\\\\\\\\\\\
            # _____________________________________________
            # _____________________________________________

            # Channel-related entries
            # Un-comment this next line if your bot should be active in all channels he's invited in
            channel_id = message.get('channel')
            channel_name = await api_call('channels.info',  # gets the name of the channel for given id
                                          {'channel': channel_id})  # doesn't work all the time

            # Team-related entries
            team_id = self.rtm['team']['id']  # gets id of the active team
            team_name = self.rtm['team']['name']  # gets name of the active team

            # User-related entries
            user_id = message.get('user')
            user_name = await api_call('users.info',  # gets user name based on id
                                       {'user': user_id})

            # Self-related entries
            bot_id = self.rtm['self']['id']  # gets id of self, meaning the bot.
            bot_name = self.rtm['self']['name'] # gets its name

            # message related entries
            message_text = message.get('text')
            # Prints input message. May contain useful information for coding, debugging, etc.
            # print("message : {0}".format(message))

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
                    response_text = action()
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    bot = PictBot(TOKEN)
    loop.run_until_complete(bot.connect())
    loop.close()
