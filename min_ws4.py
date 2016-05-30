import asyncio
import logging

import simplejson as json

import secure_auth

__author__ = 'schien'

import websocket

import asyncio
import logging

logger = logging.getLogger(__name__)

is_alive = True


async def alive():
    while is_alive:
        logger.info('alive')
        await asyncio.sleep(300)


import asyncio
import websockets


async def hello():
    ak, ak_id = secure_auth.get_auth_tokens()
    ws_url = secure_auth.get_websocket_url(ak, ak_id)
    websocket = await websockets.connect(ws_url)

    while True:
        message = await websocket.recv()
        # print(message)
        res = json.loads(message)
        print(res)


asyncio.get_event_loop().run_until_complete(asyncio.wait([
    alive(),
    hello()
]))
