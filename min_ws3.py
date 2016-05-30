import asyncio
import logging

import simplejson as json

import secure_auth

__author__ = 'schien'

logger = logging.getLogger(__name__)


class ConnectionException(Exception):
    pass


import websocket


@asyncio.coroutine
def handle_recv(ws):
    yield from ws.recv()


async def alive(websocket):
    while is_alive:
        logger.info('Secure importer alive. Connection state: %s' % websocket.state_name)
        await asyncio.sleep(300)


is_alive = False

if __name__ == "__main__":
    # secure_client.delete_auth_tokens()

    ak, ak_id = secure_auth.get_auth_tokens()
    ws_url = secure_auth.get_websocket_url(ak, ak_id)
    ws = websocket.create_connection(ws_url)
    is_alive = True
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(handle_recv(ws)), asyncio.ensure_future(alive(ws))]
    try:
        logger.debug("starting event loop")
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        pass

    # print("Sending 'Hello, World'...")
    # ws.send("Hello, World")
    # print("Sent")
    # print("Receiving...")
    result = ws.recv()
    print("Received {}".format(result))

    res = json.loads(result)
    logger.debug("Received push message from websocket", extra={'data': res})
    # if res['DataType'] == 0:
    # process_push_data(res['Data'])
