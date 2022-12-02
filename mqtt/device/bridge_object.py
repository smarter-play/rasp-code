import asyncio
import logging
import uuid
import shortuuid

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
        self.basket_topic = "{0}/{1}/{2}/{3}/".format(
            mqttParams.BASE_TOPIC,
            mqttParams.COURT_TOPIC,
            self.id,
            mqttParams.BASKET_TOPIC,
        )

    async def start_tcp_server(self):
        """
        Start TCP server
        """
        try:
            server = await asyncio.start_server(
                self.handle_client, bridgeInfo.address, bridgeInfo.port
            )
            logging.info(f"Server listening at {bridgeInfo.address}:{bridgeInfo.port}")
            async with server:
                await server.serve_forever()
        except Exception as e:
            logging.error(f"{self.id} failed to start TCP server: {e}")

    async def handle_client(self, reader, writer):
        """
        Callback function to handle client
        """
        request = await reader.read(32)
        if not request:
            return
        address = writer.get_extra_info("peername")[0]

        logging.info(f"{self.id} received {request} from {address}")

        request_type = request[0]
        id = request[1:5].decode("utf-8", "ignore")
        payload = request[5:]

        if request_type == packetStructures.SCORE_CODE:
            self.on_score(id)
        elif request_type == packetStructures.ACCELEROMETER_CODE:
            self.on_accelerometer(id, *payload[0:7])
        elif request_type == packetStructures.CUSTOM_BUTTON_CODE:
            self.custom_button(id, payload[0])
        else:
            logging.error(f"Unknown request from {address}: {request}")

    async def on_connect(self):
        """
        Connect to mqtt broker
        Publish retained device info message
        """
        try:
            # logging.info(f"{self.id} connected to MQTT broker")
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
        if topic and message:
            try:
                async with self.mqtt_client:
                    await self.mqtt_client.publish(topic, message)
                logging.info(f"{self.id} published to topic {topic}: {message}")
            except Exception as e:
                logging.error(f"{self.id} failed to publish to topic {topic}: {e}")
        else:
            logging.error(f"{self.id} failed to publish to topic {topic}: {message}")

    def on_score(self, id):
        """
        Compose and publish basket data message
        :param  id: id of the client
        """
        try:

            logging.info(f"{self.id} received score from {id}")
            message = GenericMessage("SCORE", [id])
            asyncio.get_event_loop().create_task(
                self.publish_data(
                    topic=self.basket_topic + id,
                    message=message.to_json(),
                )
            )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    def on_accelerometer(self, id, accX, accY, accZ, gyroX, gyroY, gyroZ, temp):
        """
        Compose and publish accelerometer data message
        :id: id of the client
        :accX: accelerometer x value
        :accY: accelerometer y value
        :accZ: accelerometer z value
        :gyroX: gyroscope x value
        :gyroY: gyroscope y value
        :gyroZ: gyroscope z value
        :temp: temperature value
        """
        try:
            message = GenericMessage(
                "ACCELEROMETER", [id, accX, accY, accZ, gyroX, gyroY, gyroZ, temp]
            )
            asyncio.get_event_loop().create_task(
                self.publish_data(
                    topic=self.basket_topic + id,
                    message=message.to_json(),
                )
            )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    def custom_button(self, address, buttonIdX):
        """
        Custom command
        :button idX: id of the button
        """
        try:
            message = GenericMessage("ACCELEROMETER", [address, [buttonIdX]])
            asyncio.get_event_loop().create_task(
                self.publish_data(
                    topic=self.basket_topic,
                    message=message.to_json(),
                )
            )
        except Exception as e:
            logging.error(
                f"{self.id} failed to publish to topic {self.basket_topic}: {e}"
            )

    async def start(self):
        try:
            logging.info(f"{self.id} bridge device starting")
            await self.on_connect()
            await self.start_tcp_server()

        except Exception as e:
            logging.error(f"{self.id} bridge device failed to start: {e}")
