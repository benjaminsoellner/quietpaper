import datetime
import socket
import os

def check_socket(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, port))
        return result
    except:
        return False

class MonitorWidget:

    def __init__(self, nas_host, vpn_host, x, y):
        self.x = x
        self.y = y
        self.vpn_host = vpn_host
        self.nas_host = nas_host
        self.nas_ok = False
        self.vpn_ok = False
        self.inet_ok = False

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        self.nas_ok = (check_socket(self.nas_host, 80) == 0)
        self.vpn_ok = (os.system("ping -c 1 %s >/dev/null 2>/dev/null" % self.vpn_host) == 0)
        self.inet_ok = (check_socket("www.google.com", 80) == 0)
        
    def get_retrieve_rate(self, cycle):
        return 1
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+196, y+32)
        if self.nas_ok:
            display.bmp(x, y, "icons/monitor_nas.gif")
        if not self.vpn_ok:
            display.bmp(x, y+11, "icons/monitor_vpn.gif", is_red=True)
        if not self.inet_ok:
            display.bmp(x, y+21, "icons/monitor_inet.gif", is_red=True)