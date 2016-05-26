"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp
import random

from api import api_call
from config import DEBUG, TOKEN


# Pour le moment, le bot :
#   -Ne répond que lorsqu'on s'addresse à lui, sous forme de texte.
#   -Répond aux commandes pic, picture et help.
#   -Dirige les utilisateurs vers la commande help si aucune bonne commande entrée.

#   -TO DO: Faire en sorte que le bot upload une image du répertoire "Images" en réponse aux commandes pic et picture.

# Liens utiles :
#   -Méthodes disponibles pour api_call : https://api.slack.com/methods
#   -Guide du prof : https://medium.com/@greut/a-slack-bot-with-pythons-3-5-asyncio-ad766d8b5d8f#.7okn8gngi

class PictBot:
    def __init__(self, token=TOKEN):
        self.token = token
        self.rtm = None
        self.api = {
            "pic": self.picture,
            "picture": self.picture,
            "joke": self.joke,
            "help": self.help
        }

        self.jokes = [
            "Knock, Knock \n - Who's there? \n - Your Java Update",
            "Knock, Knock \n - Who's there? \n *Long Pause* \n - Java",
            "A SQL query goes into a bar, walks up to two tables and asks, 'Can I join you?'",
            "When your hammer is C++, everything begins to look like a thumb.",
            "programmer (noun) An organism capable of converting caffeine into code."
        ]

    async def sendText(self, message, channel_id, user_name, team_id, *args):
        return await api_call('chat.postMessage', {"type": "message",
                                                   "channel": channel_id,
                                                   "text": "<@{0}> {1}".format(user_name["user"]["name"], message),
                                                   "team": team_id})

    async def joke(self, channel_id, user_name, team_id, *args):
        return await self.sendText(random.choice(self.jokes), channel_id, user_name, team_id, *args)

    async def picture(self, channel_id, user_name, team_id, file_path, name_of_file):
        with open(file_path, 'rb') as f:
            file_uploaded = await api_call('files.upload',
                                           {"channel": channel_id,
                                            "team": team_id,
                                            "text": "<@{0}>".format(user_name["user"]["name"]),
                                            "filename": name_of_file},
                                           file=f
                                           )
            return file_uploaded

    async def help(self, channel_id, user_name, team_id, *args):
        helpMessage = "Welcome to our Picture bot ! \n" \
                      "This bot is here to send you some funny pictures from some funny websites. \n" \
                      "Here are the commands : \n" \
                      " - pic : uploads a picture. \n" \
                      " - picture : one and the same =P \n" \
                      " - joke : gets you a random joke for you, programmer" \
                      " - help : I think you already know this one, don't you. \n" \
                      "Have fun !"
        return await self.sendText(helpMessage, channel_id, user_name, team_id)

    async def error(self, channel_id, user_name, team_id, *args):
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
                                          {'channel': message.get('channel')}) # doesn't work for some reason

            # Team-related entries
            team_id = self.rtm['team']['id']  # gets id of the active team
            team_name = self.rtm['team']['name']  # gets name of the active team

            # User-related entries
            user_id = message.get('user')
            user_name = await api_call('users.info',  # gets user name based on id
                                       {'user': message.get('user')})

            # Self-related entries
            bot_id = self.rtm['self']['id']  # get id of self, meaning the bot.
            bot_name = await api_call('users.info',  # gets the name of self
                                      {'user': bot_id})

            # Prints input message. May contain useful information for coding, debugging, etc.
            print("message : {0}".format(message))

            # _____________________________________________
            # _____________________________________________
            # ///////////ANSWER DECISION MAKING\\\\\\\\\\\\
            # _____________________________________________
            # _____________________________________________

            # Splits message in half, with recipient on the left side, and the core text on the other.
            message_split = message.get('text').split(':', 1)
            recipient = message_split[0].strip()

            if len(message_split) > 0 and recipient == '<@{0}>'.format(bot_id):  # If message is adressed to our bot
                core_text = message_split[1].strip()
                print(await self.api.setdefault(core_text, self.error)(channel_id,
                                                                       user_name,
                                                                       team_id,
                                                                       'Images/meme1.jpg',
                                                                       'pic.png'))

    async def connect(self):
        """Create a bot that joins Slack."""

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
