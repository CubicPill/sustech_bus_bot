import time


def parse_overrides(f):
    pass


class BusSchedule:
    def __init__(self, folder, override=None):
        self.override_file = override

    def get_next(self, t=time.time()):
        pass
