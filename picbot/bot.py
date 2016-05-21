"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp

from api import api_call
from config import DEBUG, TOKEN

async def consumer(message, ws):
    """Consume the message by printing them."""
    print(message)
    if message.get('type') == 'message' and message.get('channel') == 'G1AN77A0L':
        user = await api_call('users.info',
                              {'user': message.get('user')})

        channel = "G1AN77A0L"
        team = "T0LPWE4R5"

        mSplit = message.get('text').split(':', 1)
        adressedTo = mSplit[0]
        coreText = mSplit[1]

        if(adressedTo == '<@U145RGCDS>'):
            answer = bot_answers(coreText.strip())
            ws.send_str(json.dumps({"type": "message",
                                "channel": channel,
                                "text": "<@{0}> {1}".format(user["user"]["name"], answer),
                                "team": team}))
            #uploaded = await api_call('files.upload', {'file': 'Images/meme1.jpg',
            #                                           "channel": channel,
            #                                           "team": team})


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
