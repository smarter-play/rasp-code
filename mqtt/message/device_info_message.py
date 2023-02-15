import json
from mqtt.message.generic_message import GenericMessage


class DeviceInfoMessage(GenericMessage):
    def __init__(self, id, city, manufacturer, software_version):
        super().__init__("INFO", [str(id), city, manufacturer, software_version])
    
    def to_json(self):
        return super().to_json()