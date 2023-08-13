import datetime
from quietpaper import logger

class LaundryMachine:
    def __init__(self, plug_name, meross_connection, stby_power, active_power):
        self.plug_name = plug_name
        self.meross_connection = meross_connection
        self.stby_power = stby_power
        self.active_power = active_power
        self.last_active = None
    
    def get_state(self):
        power = self.meross_connection.get_power_of_plug(self.plug_name)
        logger.info("Power of " + self.plug_name + " is " + str(power))
        if (power is not None and power > self.stby_power):
            if power > self.active_power:
                self.last_active = datetime.datetime.now()
                return "active"
            else:
                # negative value for standby means that value is so low in standby that it cannot be measured
                # --> interpret it as number of minutes to show "standby" after machine is done
                if self.stby_power < 0:
                    if self.last_active is not None and \
                            (self.last_active - datetime.datetime.now()) < datetime.timedelta(minutes=-self.stby_power):
                        return "stby"
                    else:
                        return None
                else:
                    return "stby"
        else:
            return None

class LaundryWidget:

    def __init__(self, x, y, washing_machine, drying_machine, meross_connection):
        self.x = x
        self.y = y
        self.washing_machine = washing_machine
        self.washing_state = None
        self.drying_machine = drying_machine
        self.drying_state = None
        self.meross_connection = meross_connection
       
    def initialize(self):
        pass

    def retrieve(self, cycle):
        self.meross_connection.connect()
        self.washing_state = self.washing_machine.get_state()
        self.drying_state = self.drying_machine.get_state()
        self.meross_connection.disconnect()

    def get_retrieve_rate(self, cycle):
        return 2
    
    def get_render_rate(self, cycle):
        return 2

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+64, y+32)
        if self.washing_state is not None:
            display.bmp(x, y, "icons/washing_%s.bmp" % self.washing_state, is_red=(self.washing_state == "stby"))
        if self.drying_state is not None:
            display.bmp(x+32, y, "icons/drying_%s.bmp" % self.drying_state, is_red=(self.drying_state == "stby"))