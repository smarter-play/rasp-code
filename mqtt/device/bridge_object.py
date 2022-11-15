import asyncio
import logging
import uuid

from asyncio_mqtt import Client

from mqtt.conf.broker_params import CloudBrokerParams as mqttParams
from mqtt.conf.bridge_info import BridgeInfo as bridgeInfo
import mqtt.message.generic_message as GenericMessage
import mqtt.message.device_info_message as DeviceInfoMessage
from mqtt.resource.photodiode_sensor_resource import PhotoDiodeSensorResource


SCORE_CODE = 0x00
ACCELEROMETER_CODE = 0x01


class BridgeObject:
    """
    Bridge Object
    Retrieve data from MCU and publish it to the cloud broker
    This code runs on Rasp
    Custom protocol to communicate with MCU
    """
    def __init__(self) -> None:
        self.id = uuid.uuid4()
        self.mqtt_client = Client(
            hostname = mqttParams.BROKER_ADDRESS,
            port = mqttParams.BROKER_PORT,
            clean_session = True,
            client_id = str(self.id),
        )

        logging.info("SmartObject created: %s", self.id)

        # Topic to publish to
        self.basket_topic = "{0}/{1}/{2}/{3}/{4}".format(
            mqttParams.BASE_TOPIC,
            mqttParams.COURT_TOPIC,
            self.id,
            mqttParams.BASKET_TOPIC,
            self.basket,
        )

    async def start_tcp_server(self):
        """
        Start TCP server
        """
        server = await asyncio.start_server(self.handle_client, bridgeInfo.address, bridgeInfo.port)
        logging.info(f"Server listening at {bridgeInfo.address}:{bridgeInfo.port}")
        async with server:
            asyncio.get_event_loop().create_task(server.serve_forever())

    async def handle_client(self, reader, writer):
        request = None
        while request != "q":
            request = (await reader.read(255))
            address = writer.get_extra_info('peername')

            logging.info(f"{self.id} received {request} from {address}")
            
            if request[0] == SCORE_CODE:
                self.on_score(address)
            elif request[0] == ACCELEROMETER_CODE:
                x = request[1]
                y = request[2]
                z = request[3]
                self.on_accelerometer(address, x, y, z)
            elif request[0] == 0x02:
                self.custom_command()
            else:
                logging.error(f"Unknown request from {address}: {request}")

    async def on_connect(self):
        """
        Connect to mqtt broker
        Publish retained device info message
        """
        try:
            await self.mqtt_client.connect()
            logging.info(f"{self.id} connected to MQTT broker")
            message = DeviceInfoMessage(self.id, 
                bridgeInfo.city,
                bridgeInfo.manufacturer,
                bridgeInfo.software_version
            )
            # Publish retained device info message
            await self.mqtt_client.publish(
                self.info_topic,
                message.to_json(),
                retain=True)
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
                await self.mqtt_client.publish(topic, message)
                logging.info(f"{self.id} published to topic {topic}: {message}")
            except Exception as e:
                logging.error(f"{self.id} failed to publish to topic {topic}: {e}")
        else:
            logging.error(f"{self.id} failed to publish to topic {topic}: {message}")
    
    def on_score(self, address):
        """
        Compose and publish basket data message
        """
        try:
            message = GenericMessage("SCORE", [address, 1])
            asyncio.get_event_loop().create_task(self.publish_data(
                topic=self.basket_topic,
                message=message.to_json(),
            ))
        except Exception as e:
            logging.error(f"{self.id} failed to publish to topic {self.basket_topic}: {e}")

    def on_accelerometer(self, address, x, y, z):
        """
        Compose and publish accelerometer data message
        """
        try:
            message = GenericMessage("ACCELEROMETER", [address, [x, y, z]])
            asyncio.get_event_loop().create_task(self.publish_data(
                topic=self.basket_topic,
                message=message.to_json(),
            ))
        except Exception as e:
            logging.error(f"{self.id} failed to publish to topic {self.basket_topic}: {e}")

    def custom_command(self):
        """
        Custom command
        """
        pass
