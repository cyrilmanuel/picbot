"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp

from api import api_call
from config import DEBUG, TOKEN


# C'est dans consumer que l'essentiel du traitement des messages se fait.

# Pour le moment, le bot :
#   -Ne répond que lorsqu'on s'addresse à lui, sous forme de texte.
#   -Répond aux commandes pic, picture, insult et help.
#   -Dirige les utilisateurs vers la commande help si aucune bonne commande entrée.

#   -TO DO: Faire en sorte que le bot upload une image du répertoire "Images" en réponse aux commandes pic et picture.
async def consumer(message, ws):
    """Consume the message by printing them."""
    channel = "G1AN77A0L"
    team = "T0LPWE4R5"
    id_bot = "U145RGCDS"
    print(message)

    if message.get('type') == 'message' and message.get('channel') == channel:
        user = await api_call('users.info',  # récupère le nom de l'utilisateur ayant envoyé le message
                              {'user': message.get('user')})

        # sépare le message en deux, avec d'un côté le destinataire du message, de l'autre le corps du message.
        message_split = message.get('text').split(':', 1)
        recipient = message_split[0]

        if len(message_split) > 0 and recipient == '<@{0}>'.format(id_bot):
            core_text = message_split[1]

            answer = bot_answers(
                    core_text.strip())  # La methode "strip()" enlève les espaces superflus ("   picture  " sera considéré comme "picture")

            # la méthode ci-dessous envoie sur le web socket un message sous forme de string.
            ws.send_str(json.dumps({"type": "message",
                                    "channel": channel,
                                    "text": "<@{0}> {1}".format(user["user"]["name"], answer),
                                    "team": team}))

            with open('Images/meme1.jpg', 'rb') as f:
                file_uploaded = await api_call('files.upload',
                                               {"channel": channel, "team": team, "filename": 'picONON.png', "file": f}
                                               )
                print(file_uploaded['file']['permalink'])

                await api_call('chat.postMessage',
                               {"channel": channel,
                                "text": "image",
                                "attachments": [
                                    {
                                        "fallback": "Required plain-text summary of the attachment.",
                                        "title": "Slack API Documentation",
                                        "color": "#ff70ff",
                                        "image_url": "http://img.hebus.com/hebus_2016/05/18/1463547427_92448.jpg"
                                    }
                                ],
                                "as_user": "true"
                                }
                               )


# Retourne un message en fonction du message entré, avec une valeur par défaut si x n'est pas pris en charge.
def bot_answers(x):
    return {
        'pic': 'The picture module is still in development.',
        'picture': 'The picture module is still in development.',
        'insult': "Darn, thee are quite as beautiful as a slug's arse, Sir.",
        'help': "Welcome to using our pictbot ! \n"
                "This bot's purpose is to upload you some funny pictures when you ask fort it.\n"
                "Command 'pic' : Uploads a picture.\n"
                "Command 'picture' : same as above.\n"
                "Command 'insult' : insults you like a Sir.\n"
                "Command 'help' : you know what this does.\n",
    }.get(x, 'Command not found. Type "help" for a list of commands available.')


async def bot(token):
    """Create a bot that joins Slack."""
    loop = asyncio.get_event_loop()
    with aiohttp.ClientSession(loop=loop) as client:
        async with client.post("https://slack.com/api/rtm.start",
                               data={"token": TOKEN}) as response:
            assert 200 == response.status, "Error connecting to RTM."
            rtm = await response.json()

        async with client.ws_connect(rtm["url"]) as ws:
            async for msg in ws:
                assert msg.tp == aiohttp.MsgType.text
                message = json.loads(msg.data)
                asyncio.ensure_future(consumer(message, ws))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    loop.run_until_complete(bot(TOKEN))
    loop.close()
