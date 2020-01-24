
from meross_iot.cloud.devices.power_plugs import GenericPlug
from meross_iot.manager import MerossManager

class MerossConnection:
    def __init__(self, meross_email, meross_password):
        self.manager = MerossManager(meross_email=meross_email, meross_password=meross_password)
        self.manager.start()

    def get_plug_by_name(self, name):
        for p in self.manager.get_devices_by_kind(GenericPlug):
            if p.name == name:
                return p   
        return None