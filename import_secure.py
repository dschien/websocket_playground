import asyncio
import logging

import simplejson as json
import time
import websockets


__author__ = 'schien'

logger = logging.getLogger(__name__)


class ConnectionException(Exception):
    pass


class Command(BaseCommand):
    help = 'Import now'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--reset-mc', action='store_true', default=False)

    def handle(self, *args, **options):

        loop = asyncio.get_event_loop()
        self.tasks = [
            asyncio.ensure_future(self.listen_for_event_messages(options, loop)),
        ]
        try:
            logger.debug("starting event loop")
            loop.run_until_complete(asyncio.wait(self.tasks))
        except KeyboardInterrupt:
            pass

    is_alive = False

    async def alive(self, websocket):
        while self.is_alive:
            logger.info('Secure importer alive. Connection state: %s' % websocket.state_name)
            await asyncio.sleep(300)

    @asyncio.coroutine
    def listen_for_event_messages(self, options, loop):
        attempts = 10
        websocket = None
        while not websocket and attempts > 0:
            try:
                if options['reset_mc']:
                    secure_client.delete_auth_tokens()

                ak, ak_id = secure_client.get_auth_tokens()
                ws_url = secure_client.get_websocket_url(ak, ak_id)
                websocket = yield from websockets.connect(ws_url)
            except Exception as e:

                attempts -= 1
                logger.error(e)
                logger.error("Attempt failed to connect to Secure Systems websocket server")
                time.sleep(1)

        if not websocket:
            raise Exception("Could not connect to Secure Systems websocket server.")

        try:
            self.is_alive = True

            self.tasks.append(asyncio.ensure_future(self.alive(websocket)))
            while True:
                try:
                    message = yield from websocket.recv()
                    res = json.loads(message)
                    logger.debug("Received push message from websocket", extra={'data': res})
                    if res['DataType'] == 0:
                        process_push_data(res['Data'])
                    else:
                        logger.info("Received error from websocket", extra={'data': res})
                        logger.info("Restarting websocket listener")
                        yield from websocket.close()

                        secure_client.delete_auth_tokens()

                        ak, ak_id = secure_client.get_auth_tokens()
                        ws_url = secure_client.get_websocket_url(ak, ak_id)
                        websocket = yield from websockets.connect(ws_url)

                except Exception as e:
                    logger.warn('ConnectionClosed %s' % e)
                    self.is_alive = False
                    break
        except Exception as e:
            logger.warn('Could not connect: %s' % e)

        finally:
            logger.warn("Importer is stopping")
            if websocket:
                yield from websocket.close()
            self.is_alive = False
