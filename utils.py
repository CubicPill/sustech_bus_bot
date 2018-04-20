import time
import datetime
import os
from enum import Enum


class DayType(Enum):
    WEEKEND = 'WEEKEND'
    WEEKDAY = 'WEEKDAY'


class BusLine:
    def __init__(self, id, name, day, route, time_list):
        self.id = id
        self.name = name
        self.day = day
        self.route = route
        self.time_list = time_list  # this must be sorted!

    @staticmethod
    def bin_search(time_list: list, t_int: int) -> int:
        i, j = 0, len(time_list) - 1
        while i != j:
            mid = int((i + j) / 2)
            if t_int < time_list[mid]:
                j = mid
            else:
                i = mid + 1
        return time_list[i]

    def get_next(self, t_int: int) -> int:
        if t_int > self.time_list[-1]:  # if is after the last bus of the day, return the first bus tomorrow
            return self.time_list[0]
        return self.bin_search(self.time_list, t_int)


class BusSchedule:
    def __init__(self, folder, override=None):
        self.folder = folder
        self.override_file = override
        self.line_details = list()
        self.override_detail = list()

    def _read_line_info(self):
        for filename in os.listdir(self.folder):
            print(filename)
            with open(os.path.join(self.folder, filename)) as f:
                self.line_details.append(self.parse_line(f.readlines()))

    @staticmethod
    def parse_overrides(lines: list):
        pass

    @staticmethod
    def parse_line(lines: list) -> BusLine:
        # the line configuration files' line breaking should be UNIX-Style
        lines = [l for l in lines if l and '\n' != l]
        try:
            assert lines[0].startswith('id:')
            assert lines[1].startswith('name:')
            assert lines[2].startswith('day:')
            assert lines[3].startswith('route:')
        except AssertionError:
            raise ValueError('Invalid line configuration data')
        result = {
            'id': lines[0].split(':', 1)[-1],
            'name': lines[1].split(':', 1)[-1],
            'day': DayType.WEEKDAY if lines[2].split(':', 1)[-1] == 'weekday' else DayType.WEEKEND,
            'route': lines[3].split(':', 1)[-1],
            'time_list': list()
        }
        for l in lines[4:]:
            result['time_list'].append(int(''.join(l.split(':'))))
        result['time_list'].sort()
        return BusLine(**result)

    def get_all_lines_next(self, t=time.time()):
        t_int = int(time.strftime('%H%M', time.localtime(t)))
        for line in self.line_details:
            line.get_next(t_int)

    def get_line_detail(self, line_id):
        pass

    def get_all_lines(self):
        pass
