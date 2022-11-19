import logging
import asyncio


from mqtt.device.bridge_object import BridgeObject
from mqtt.resource.photodiode_sensor_resource import PhotoDiodeSensorResource

async def main():
    try:
        bridge = BridgeObject()
        mcu = PhotoDiodeSensorResource()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().create_task(mcu.start_periodic_update())
        await bridge.start()
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())