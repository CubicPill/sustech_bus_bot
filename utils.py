import time
import datetime
import os
from enum import IntEnum


class QueryStatus(IntEnum):
    MISS_LAST = -1
    NOT_TODAY = -2


class BusLine:
    def __init__(self, id, name, group, day, route, time_list):
        self._id = id
        self._name = name
        self._group = group
        self._day = day
        self._route = route
        self._time_list = time_list  # this must be sorted!

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def group(self):
        return self._group

    @property
    def day(self):
        return self._day

    @property
    def route(self):
        return self._route

    @property
    def time_list(self):
        return self._time_list

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
        dt = datetime.datetime.fromtimestamp(ts)
        if dt.weekday() + 1 not in self._day:  # today this line is not running
            return QueryStatus.NOT_TODAY
        t_int = int(time.strftime('%H%M', time.localtime(ts)))
        if t_int > self._time_list[-1]:  # if is after the last bus of the day
            return QueryStatus.MISS_LAST
        return self.bin_search(self._time_list, t_int)

    def add_override(self):
        pass


class BusSchedule:
    def __init__(self):

        self._lines = dict()
        self._groups = dict()
        self._read_line_info()

    def _read_line_info(self):
        for filename in os.listdir('./lines'):
            with open(os.path.join('./lines', filename), encoding='utf8') as f:
                l = self.parse_line(f.readlines())
                self._lines[l.id] = l

        with open('./date_override.txt', encoding='utf8') as f:
            self.parse_overrides(f.readlines())
        with open('group_def.txt', encoding='utf8') as f:
            for line in f.readlines():
                if line:
                    group, description = line.split(':')
                    self._groups[group] = description

    @staticmethod
    def parse_overrides(lines: list):
        lines = [l for l in lines if l and '\n' != l and not l.startswith('#')]
        return [l.split(' ', 1) for l in lines]

    @staticmethod
    def parse_line(lines: list) -> BusLine:
        # the line configuration files' line breaking should be UNIX-Style
        lines = [l.replace('\n', '') for l in lines if l and '\n' != l and not l.startswith('#')]
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
            'day': [int(i) for i in lines[3].split(':', 1)[-1].split(',')],
            'route': lines[4].split(':', 1)[-1],
            'time_list': list()
        }
        for l in lines[5:]:
            result['time_list'].append(int(''.join(l.split(':'))))
        result['time_list'].sort()

        return BusLine(**result)

    def get_all_lines_next(self, t=time.time()):
        """
        get next bus on all groups of lines
        in-group priority: latest > miss_last > not_today

        :param t: timestamp
        :return: dict
        """
        results = dict()
        for line in self._lines.values():
            r = line.get_next(t)
            if results.get(line.group) is not None:
                if results[line.group][0] == QueryStatus.NOT_TODAY:
                    # every result can override NOT_TODAY
                    results[line.group] = [r, line.id]
                elif results[line.group][0] == QueryStatus.MISS_LAST:
                    # if result is not NOT_TODAY, every result can override MISS_LAST
                    if r != QueryStatus.NOT_TODAY:
                        results[line.group] = [r, line.id]
                else:
                    # if is a time result, take the latest
                    if results[line.group][0] > r >= 0:
                        results[line.group] = [r, line.id]
            else:
                results[line.group] = [r, line.id]
        return results

    def get_line(self, line_id):
        return self._lines.get(line_id)

    def get_all_lines_id(self):
        return list(self._lines.keys())

    def get_group_def(self, group_id):
        return self._groups.get(group_id)
