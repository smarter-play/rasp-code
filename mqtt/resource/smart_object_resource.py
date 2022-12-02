import logging
 

class SmartObjectResource:
    def __init__(self, object_id, object_type) -> None:
        self.object_id = object_id
        self.object_type = object_type

    async def notify_update(self, updated_value, **kwargs):
        logging.debug("notify_update: %s", updated_value)
        if self.resource_data_listener:
            self.resource_data_listener(updated_value, **kwargs)
        else:
            logging.info("No listener for resource %s", self.object_id)

    def add_data_listener(self, listener):
        self.resource_data_listener.append(listener)
    
    def remove_data_listener(self, listener):
        if self.resource_data_listener and listener in self.resource_data_listener:
            self.resource_data_listener.remove(listener)
        else:
            logging.info("No listener for resource %s", self.object_id)
            