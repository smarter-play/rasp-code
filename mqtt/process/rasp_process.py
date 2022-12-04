### USE THIS TO RUN BRIDGE OBJECT ###

import logging
import asyncio

from mqtt.device.bridge_object import BridgeObject
from mqtt.resource.photodiode_sensor_resource import PhotoDiodeSensorResource


async def main():
    try:
        bridge = BridgeObject()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        await bridge.start()
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
