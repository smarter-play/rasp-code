import asyncio
import logging
import random
import struct
import sys

PACKET_TYPE_SCORE = 0x00
PACKET_TYPE_ACCELEROMETER_DATA = 0x01
PACKET_TYPE_CUSTOM_BUTTON = 0x02

class Simulator:
    def send_score(self, basket_id, writer):
        writer.write(struct.pack('B', PACKET_TYPE_SCORE))
        writer.write(struct.pack('I', basket_id))
        # No payload
        
        logging.debug(f"{basket_id} - Sent score")

    def send_accelerometer_data(self, basket_id, writer):
        writer.write(struct.pack('B', PACKET_TYPE_ACCELEROMETER_DATA))
        writer.write(struct.pack('I', basket_id))

        accelerometer_data = [random.uniform(-100, 100) for _ in range(7)]
        writer.write(struct.pack('fffffff', *accelerometer_data))
        
        logging.debug(f"{basket_id} - Sent accelerometer data: {accelerometer_data}")

    def send_custom_button(self, basket_id, writer):
        writer.write(struct.pack('B', PACKET_TYPE_CUSTOM_BUTTON))
        writer.write(struct.pack('I', basket_id))

        custom_button_idx = random.randint(0, 3)
        writer.write(struct.pack('I', custom_button_idx))
        
        logging.debug(f"{basket_id} - Sent custom button: {custom_button_idx}")

    async def start(self, address, port):
        logging.info(f"Connecting to {address}:{port}...")

        _, writer = await asyncio.open_connection(address, port)

        logging.info(f"Connected")

        basket_id = random.getrandbits(32)

        logging.info(f"Generated basket ID: {basket_id}")

        while True:
            send_packet_functions = [
                self.send_score,
                self.send_accelerometer_data,
                self.send_custom_button
            ]
            send_packet_function = send_packet_functions[random.randrange(len(send_packet_functions))]
            send_packet_function(basket_id, writer)

            await writer.drain()

# ------------------------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------------------------

async def main():
    simulator = Simulator()
    await simulator.start("localhost", 2323)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    asyncio.run(main())