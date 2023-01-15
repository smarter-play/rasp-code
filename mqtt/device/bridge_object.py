import asyncio
import logging
import uuid
import struct

import asyncio_mqtt as aiomqtt

from mqtt.conf.broker_params import CloudBrokerParams as mqttParams
from mqtt.conf.bridge_info import BridgeInfo as bridgeInfo
from mqtt.message.device_info_message import DeviceInfoMessage
from mqtt.message.generic_message import GenericMessage
from mqtt.conf.packet_structures import TCPPacketStructures as packetStructures

class BridgeObject:
    """
    Bridge Object
    Retrieve data from MCU and publish it to the cloud broker
    This code runs on Rasp
    Custom protocol to communicate with MCU
    """

    def __init__(self) -> None:
        self.id = str(uuid.uuid4())
        self.mqtt_client = aiomqtt.Client(
            hostname=mqttParams.BROKER_ADDRESS,
            port=mqttParams.BROKER_PORT,
            clean_session=True,
            client_id=str(self.id),
        )

        logging.info("SmartObject created: %s", self.id)

        # Topic to publish to
        self.basket_topic = "{0}/{1}/".format(
            mqttParams.BASE_TOPIC,
            mqttParams.BASKET_TOPIC,
            # + id_canestro
        )

    async def start_tcp_server(self):
        """
        Start TCP server
        """
        try:
            server = await asyncio.start_server(
                self.handle_client,
                bridgeInfo.address,
                bridgeInfo.port,
            )
            logging.info(f"Server listening at {bridgeInfo.address}:{bridgeInfo.port}")
            async with server:
                await server.serve_forever()
        except Exception as e:
            logging.error(f"{self.id} failed to start TCP server: {e}")

    async def handle_client(self, reader, writer):
        """
        Callback function to handle client
        :param  reader: reader object
        :param  writer: writer object
        """

        address = writer.get_extra_info("peername")[0]

        while True:
            [packet_type] = struct.unpack('B', await reader.readexactly(1))
            [basket_id] = struct.unpack('I', await reader.readexactly(4))

            #logging.debug(f"{address} - Received packet: type={packet_type}, basket_id={basket_id}")

            if packet_type == packetStructures.SCORE_CODE:
                await self.on_score(basket_id, reader)
            elif packet_type == packetStructures.ACCELEROMETER_CODE:
                await self.on_accelerometer(basket_id, reader)
            elif packet_type == packetStructures.CUSTOM_BUTTON_CODE:
                await self.on_custom_button(basket_id, reader)
            else:
                logging.error(f"{address} - Unknown packet type: {packet_type}")


    async def on_connect(self):
        """
        Connect to mqtt broker
        Publish retained device info message
        """
        try:
            logging.info(f"{self.id} connected to MQTT broker")
            message = DeviceInfoMessage(
                self.id,
                bridgeInfo.city,
                bridgeInfo.manufacturer,
                bridgeInfo.software_version,
            )
            # Publish retained device info message
            async with self.mqtt_client:
                await self.mqtt_client.publish(
                    self.basket_topic, message.to_json(), retain=True
                )
            logging.info(
                f"{self.id} published retained device info message on topic {self.basket_topic}"
            )
        except Exception as e:
            logging.error(f"{self.id} failed to connect to MQTT broker: {e}")

    async def publish_data(self, topic, message):
        """
        Publish given message on given topic
        :param  topic: topic to publish to
        :param  message: message to publish
        """
        try:
            if topic and message:
                async with self.mqtt_client:
                    await self.mqtt_client.publish(topic, message)
                    #logging.info(f"{self.id} published to topic {topic}: {message}")
            else:
                logging.error(f"{self.id} failed to publish to topic {topic}: {message}")
        except Exception as e:
            logging.error(f"{self.id} failed to publish to topic. Error {e}")

    async def on_score(self, basket_id, reader):
        #payload = No payload!

        logging.debug(f"{basket_id} - Score")

        try:
            logging.info(f"{self.id} received score from {basket_id}")
            message = GenericMessage("SCORE", [basket_id])
            await self.publish_data(
                    topic=self.basket_topic + str(basket_id),
                    message=message.to_json(),
                )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    async def on_accelerometer(self, basket_id, reader):
        payload = await reader.readexactly(4 * 7)
        payload = [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp] = struct.unpack('fffffff', payload)

        logging.debug(f"{basket_id} - Accelerometer data: {payload}")

        try:
            message = GenericMessage(
                "ACCELEROMETER", [basket_id, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp]
            )
            await self.publish_data(
                    topic=self.basket_topic + str(basket_id),
                    message=message.to_json(),
                )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    async def on_custom_button(self, basket_id, reader):
        payload = await reader.readexactly(4)
        payload = [custom_button_idx] = struct.unpack('i', payload)

        logging.debug(f"{basket_id} - Custom button {payload}")

        try:
            message = GenericMessage("CUSTOM_BUTTON", [basket_id, [custom_button_idx]])
            await self.publish_data(
                    topic=self.basket_topic + str(basket_id),
                    message=message.to_json(),
                )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    async def start(self):
        """
        Starts Bridge Object coroutines: cloud mqtt connection & TCP Server
        """
        try:

            logging.info(f"{self.id} bridge device starting")
            await self.on_connect()
            await self.start_tcp_server()

        except Exception as e:
            logging.error(f"{self.id} bridge device failed to start: {e}")
