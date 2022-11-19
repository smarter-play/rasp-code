import asyncio
import logging
import secrets
from mqtt.conf.packet_structures import TCPPacketStructures as packetStructures

SCORE_CODE = b'\x00'
ACCELEROMETER_CODE = b'\x01'


class CustomTCPClient:

    async def run_client(self, addr, port, **kwargs):
        reader, writer = await asyncio.open_connection(addr, port)
        uid = kwargs.get("uid", secrets.token_bytes(4))
        logging.info(f"Connected to {addr}:{port}")
        message = SCORE_CODE + uid
        writer.write(message)
        await writer.drain()
        writer.close()
        await writer.wait_closed()