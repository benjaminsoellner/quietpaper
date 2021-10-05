
from meross_iot.cloud.devices.power_plugs import GenericPlug
from meross_iot.manager import MerossManager

class MerossConnection:
    def __init__(self, meross_email, meross_password):
        self.manager = None
        self.meross_email = meross_email
        self.meross_password = meross_password
        self.connect()
    
    def connect(self):
        self.disconnect()
        self.manager = MerossManager.from_email_and_password(self.meross_email, self.meross_password)
        self.manager.start()
    
    def disconnect(self):
        if self.manager is not None:
            self.manager.stop()

    def get_plug_by_name(self, name):
        for p in self.manager.get_devices_by_kind(GenericPlug):
            if p.name == name:
                return p   
        return None