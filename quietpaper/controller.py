import time
import datetime
from quietpaper.display import Display

QP_CONTROLLER_MAX_CYCLES = 60*24
QP_CONTROLLER_NIGHT_STARTS_HOUR = 0
QP_CONTROLLER_NIGHT_ENDS_HOUR = 4
QP_CONTROLLER_WORK_STARTS_HOUR = 10
QP_CONTROLLER_WORK_ENDS_HOUR = 15

class Cycle:
    
    def _night_or_work(self):
        is_work = False
        if self.started.weekday() < 4:
            is_work = self.started.hour >= QP_CONTROLLER_WORK_STARTS_HOUR and self.started.hour < QP_CONTROLLER_WORK_ENDS_HOUR
        print(is_work)
        print(self.started.hour)
        return is_work or (self.started.hour >= QP_CONTROLLER_NIGHT_STARTS_HOUR and self.started.hour < QP_CONTROLLER_NIGHT_ENDS_HOUR)

    def __init__(self, is_first, number, is_slow=None):
        self.started = datetime.datetime.now()
        self.is_first = is_first
        self.number = number % QP_CONTROLLER_MAX_CYCLES
        if is_slow is not None:
            self.is_slow = is_slow
        else:
            self.is_slow = self._night_or_work()

    @staticmethod
    def first():
        return Cycle(is_first=True, number=0)
    
    def next(self):
        return Cycle(is_first=False, number=self.number+1)

    def duration(self):
        return datetime.datetime.now()-self.started

class Controller:

    def __init__(self, display):
        self.widgets = []
        self.screens = []
        self.max_cycles = QP_CONTROLLER_MAX_CYCLES
        self.display = display

    def register_widget(self, widget):
        self.widgets.append(widget)
        widget.initialize()

    def register_screen(self, screen):
        self.screens.append(screen)

    def cycle(self, cycle):
        if cycle.is_first:
            for screen in self.screens:
                screen.clear(self.display)
        for widget in self.widgets:
            retrieve_rate = widget.get_retrieve_rate(cycle)
            render_rate = widget.get_render_rate(cycle)
            if cycle.number is None or cycle.is_first or (retrieve_rate is not None and cycle.number % retrieve_rate == 0):
                print("Retrieving " + type(widget).__name__)
                widget.retrieve(cycle)
            if cycle.number is None or cycle.is_first or (render_rate is not None and cycle.number % render_rate == 0):
                print("Rendering " + type(widget).__name__)
                widget.render(self.display, cycle)
        for screen in self.screens:
            update_rate = screen.get_update_rate(cycle)
            if cycle.number is None or cycle.is_first or (update_rate is not None and cycle.number % update_rate == 0):
                print("Updating " + type(screen).__name__)
                screen.update(self.display, cycle)

    def loop(self):
        cycle = Cycle.first()
        while True:
            print("Cycle %d..." % cycle.number)
            self.cycle(cycle)
            duration = cycle.duration().seconds
            print("Took %d seconds" % duration)
            if duration < 60:
                time.sleep(60-duration)
            cycle = cycle.next()