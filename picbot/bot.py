"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import aiohttp

from api import api_call
from config import DEBUG, TOKEN

RUNNING = True


async def producer(user, message):
    """Produce a ping message every 10 seconds."""
    # await asyncio.sleep(10)
    return json.dumps({"type": "message",
                       "channel": "C0LPX9EMN",
                       "text": "<@{0}>{1}".format(user, message),
                       "team": "T0LPWE4R5"})


async def consumer(message, ws):
    """Consume the message by printing them."""
    print(message)
    if message.get('type') == 'message':
        user = await api_call('users.info',
                              {'user': message.get('user')})

        print("{0}:{1}".format(user["user"]["name"],
                               message["text"]))
        answer = "Shut up please."
        ws.send_str(json.dumps({"type": "message",
                                "channel": "C0LPX9EMN",
                                "text": "<@{0}>{1}".format(user["user"]["name"], answer),
                                    "team": "T0LPWE4R5"}))


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
    # loop.add_signal_handler(signal.SIGINT, stop)
    loop.run_until_complete(bot(TOKEN))
    loop.close()
