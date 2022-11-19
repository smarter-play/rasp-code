import logging
import asyncio
import secrets

from mqtt.resource.smart_object_resource import SmartObjectResource
from tcp.client import CustomTCPClient

TASK_DELAY = 5

class PhotoDiodeSensorResource(SmartObjectResource):
    def __init__(self) -> None:
        super().__init__(secrets.token_bytes(4), "photodiode_sensor")
        self.tcp_client = CustomTCPClient()

    async def start_periodic_update(self):
        try:
            logging.info(f"MCU {self.object_id} started periodic update")
            await asyncio.sleep(TASK_DELAY)
            while True:
                await self.tcp_client.run_client("localhost", 2323, uid=self.object_id)
                logging.info(f"MCU {self.object_id} updated")
                await asyncio.sleep(TASK_DELAY)
        except Exception as e:
            logging.error(f"{self.object_id} failed to start periodic update: {e}")

    def change_state(self):
        self.is_active = not self.is_active
