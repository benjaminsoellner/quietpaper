import datetime
from quietpaper import logger

class LaundryMachine:
    def __init__(self, name, meross_connection, stby_power, active_power):
        self.name = name
        self.connection = meross_connection
        self.stby_power = stby_power
        self.active_power = active_power
        self.last_active = None
        self.plug = None
    
    def reconnect(self):
        self.connection.connect()

    def refresh_plug(self):
        self.plug = self.connection.get_plug_by_name(self.name)
        if self.plug == None:
            return True

    def get_power(self):
        if self.plug is None:
            self.refresh_plug()
        if self.plug is not None:
            electricity = self.plug.get_electricity()
            if electricity and "power" in electricity and "config" in electricity:
                return electricity["power"] / electricity["config"]["electricityRatio"]
            else:
                return None
        else:
            return None

    def get_state(self):
        power = self.get_power()
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

    def __init__(self, x, y, washing_machine, drying_machine):
        self.x = x
        self.y = y
        self.washing_machine = washing_machine
        self.washing_state = None
        self.drying_machine = drying_machine
        self.drying_state = None
       
    def initialize(self):
        pass

    def retrieve(self, cycle):
        try:
            self.washing_state = self.washing_machine.get_state()
        except Exception as e: 
            logger.warning("Cannot retrieve LaundryWidget.washing_state: " + (e.message if hasattr(e, 'message') else type(e).__name__))
            self.washing_machine.restart()
            try:
                self.washing_machine.reconnect()
                self.washing_state = self.washing_machine.get_state()
            except Exception as ee:
                logger.warning("After resetting connection, still cannot retrieve LaundryWidget.washing_state: " + (ee.message if hasattr(ee, 'message') else type(ee).__name__))
        try:
            self.drying_state = self.drying_machine.get_state()
        except Exception as e:
            logger.warning("Cannot retrieve LaundryWidget.drying_state: " + (e.message if hasattr(e, 'message') else type(e).__name__))
            try:
                self.drying_machine.reconnect()
                self.drying_state = self.drying_machine.get_state()
            except Exception as ee:
                logger.warning("After resetting connection, still cannot retrieve LaundryWidget.drying_state: " + (ee.message if hasattr(ee, 'message') else type(ee).__name__))


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