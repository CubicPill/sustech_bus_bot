import time
import datetime
import os
from enum import IntEnum


class QueryStatus(IntEnum):
    MISS_LAST = -1
    NOT_TODAY = -2


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

    def get_next(self, ts: float) -> int:
        dt = datetime.datetime.utcfromtimestamp(ts)
        if dt.weekday() + 1 not in self.day:  # today this line is not running
            return QueryStatus.NOT_TODAY
        t_int = int(time.strftime('%H%M', time.localtime(ts)))
        if t_int > self.time_list[-1]:  # if is after the last bus of the day
            return QueryStatus.MISS_LAST
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
            assert lines[1].startswith('group:')
            assert lines[2].startswith('name:')
            assert lines[3].startswith('day:')
            assert lines[4].startswith('route:')
        except AssertionError:
            raise ValueError('Invalid line configuration data')
        result = {
            'id': lines[0].split(':', 1)[-1],
            'group': lines[1].split(':', 1)[-1],
            'name': lines[2].split(':', 1)[-1],
            'day': map(int, lines[3].split(':', 1)[-1].split(',')),
            'route': lines[4].split(':', 1)[-1],
            'time_list': list()
        }
        for l in lines[5:]:
            result['time_list'].append(int(''.join(l.split(':'))))
        result['time_list'].sort()
        return BusLine(**result)

    def get_all_lines_next(self, t=time.time()):
        for line in self.line_details:
            line.get_next(t)

    def get_line_detail(self, line_id):
        pass

    def get_all_lines(self):
        pass
