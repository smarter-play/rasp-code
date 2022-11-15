import json


class DeviceInfoMessage:
    def __init__(self, id, city, manufacturer, software_version) -> None:
        self.id = id
        self.city = city
        self.manufacturer = manufacturer
        self.software_version = software_version
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)