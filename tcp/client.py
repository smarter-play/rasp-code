### FOR TESTING ###

import asyncio
import logging
import os
import random

SCORE_CODE = b'\x00'
ACCELEROMETER_CODE = b'\x01'
CUSTOM_COMMAND_CODE = b'\x02'

CODES = [SCORE_CODE, ACCELEROMETER_CODE, CUSTOM_COMMAND_CODE]

class CustomTCPClient:
    """
    Testing purposes TCP client that sends a random message to the TCP server 
    using the following format:
    [1 byte] [4 bytes] [n bytes]
    [code]   [uid]     [payload]
    """

    async def run_client(self, addr, port, **kwargs):
        reader, writer = await asyncio.open_connection(addr, port)
        uid = kwargs.get("uid", os.urandom(4))
        logging.info(f"Connected to {addr}:{port}")
        message = random.choice(CODES) + uid + b'\x2d\x05\x03\x04\x05\x06\x07'
        writer.write(message)
        await writer.drain()
        writer.close()
        await writer.wait_closed()