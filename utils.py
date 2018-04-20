import time


def parse_overrides(f):
    pass


class BusSchedule:
    def __init__(self, folder, override=None):
        self.override_file = override

    def _read_line_info(self):
        pass

    def get_next(self, t=time.time()):
        pass

    def get_line_detail(self, line_no):
        pass

    def get_all_lines(self):
        pass
