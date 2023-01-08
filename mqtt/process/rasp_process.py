### USE THIS TO RUN BRIDGE OBJECT ###

import logging
import asyncio
import sys

from mqtt.device.bridge_object import BridgeObject
from mqtt.resource.mcu import MCU

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    try:
        bridge = BridgeObject()
        #mcu = MCU()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await bridge.start()
        #loop.create_task(mcu.start_periodic_update())
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
