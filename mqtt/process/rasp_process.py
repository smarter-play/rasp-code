### USE THIS TO RUN BRIDGE OBJECT ###

import logging
import asyncio
import sys

from mqtt.device.bridge_object import BridgeObject

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    try:
        bridge = BridgeObject()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await bridge.start()
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    asyncio.run(main())
