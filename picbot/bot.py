"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp

from api import api_call
from picbot.config import DEBUG, TOKEN

async def consumer(message, ws):
    """Consume the message by printing them."""
    if message.get('type') == 'message' and message.get('channel') == 'C0LPX9EMN':
        user = await api_call('users.info',
                              {'user': message.get('user')})

        answer = "Shut up please."
        channel = "C0LPX9EMN"
        team = "T0LPWE4R5"
        ws.send_str(json.dumps({"type": "message",
                                "channel": channel,
                                "text": "<@{0}> {1}".format(user["user"]["name"], answer),
                                "team": team}))

        #uploaded = await api_call('files.upload', {'file': 'Images/meme1.jpg',
        #                                           "channel": channel,
        #                                           "team": team})


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
