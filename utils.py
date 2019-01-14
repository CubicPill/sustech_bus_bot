import datetime
import json
import os
import time
from enum import IntEnum

from globals import get_config, get_logger

WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日', ]

config = get_config()
logger = get_logger()


class QueryStatus(IntEnum):
    MISS_LAST = -1
    NOT_TODAY = -2
    BEFORE_FIRST = -3


class BusLine:
    def __init__(self, id, name, group, day, route, time_list, date_overrides=None):
        self._id = id
        self._name = name
        self._group = group
        self._day = day
        self._route = route
        self._time_list = time_list  # this must be sorted!
        self._date_overrides = date_overrides if date_overrides else dict()

    @staticmethod
    def time_to_string(int_t: int):
        t = ['0'] * (3 - len(str(int_t))) + list(str(int_t))
        t.insert(-2, ':')
        return ''.join(t)

    def to_string(self):
        lines = list()
        lines.append('ID: ' + self._id)
        lines.append('名称: ' + self._name)
        lines.append('分组: ' + self._group)
        lines.append('运行时间: ' + ', '.join([WEEKDAYS[d - 1] for d in self._day]))
        lines.append('路线: ' + self._route)
        lines.append('发车时刻: ' + ', '.join([self.time_to_string(int_t) for int_t in self._time_list]))
        return '\n'.join(lines)

    def to_dict(self):
        return {
            'id': self._id,
            'name': self._name,
            'time': self._day,
            'route': self._route,
            'schedule': [self.time_to_string(int_t) for int_t in self._time_list]
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @property
    def date_overrides(self):
        return self._date_overrides

    @date_overrides.setter
    def date_overrides(self, value: dict):
        self._date_overrides = value

    def add_override_date(self, date: str, day: int):
        self._date_overrides[date] = day

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
        return i

    def get_day_in_week(self, ts) -> int:
        dt = datetime.datetime.fromtimestamp(ts)
        time_str = time.strftime('%Y-%m-%d', time.localtime(ts))
        if self._date_overrides.get(time_str) is not None:
            day_in_week = self._date_overrides[time_str]
        else:
            day_in_week = dt.weekday() + 1
        return day_in_week

    def get_next(self, ts: float) -> int:
        logger.debug('Entering get_next({ts})'.format(ts=ts))
        if self.get_day_in_week(ts) not in self._day:  # today this line is not running
            result = QueryStatus.NOT_TODAY
        else:
            t_int = int(time.strftime('%H%M', time.localtime(ts)))
            logger.debug('Current t_int is {t_int}'.format(t_int=t_int))

            if t_int > self._time_list[-1]:  # if is after the last bus of the day
                result = QueryStatus.MISS_LAST
            else:
                result = self.time_list[self.bin_search(self._time_list, t_int)]
        logger.debug('{id} get_next({ts})={ret}'.format(id=self._id, ts=ts, ret=result if result > 0 else str(result)))
        return result

    def get_current_en_route(self, ts: float) -> int:
        logger.debug('Entering get_current_en_route({ts})'.format(ts=ts))
        if self.get_day_in_week(ts) not in self._day:  # today this line is not running
            result = QueryStatus.NOT_TODAY
        else:
            t_int = int(time.strftime('%H%M', time.localtime(ts)))
            logger.debug('Current t_int is {t_int}'.format(t_int=t_int))

            if t_int < self._time_list[0]:  # if is before the first bus of the day
                result = QueryStatus.BEFORE_FIRST
            elif t_int > self._time_list[-1]:
                result = self._time_list[-1]
            else:
                result = self.time_list[self.bin_search(self._time_list, t_int) - 1]
        logger.debug('{id} get_current_en_route({ts})={ret}'.format(id=self._id, ts=ts,
                                                                    ret=result if result > 0 else str(result)))
        return result


class BusSchedule:
    def __init__(self):

        self._lines = dict()
        self._groups = dict()
        self._date_overrides = dict()
        self._read_line_info()

    def _read_line_info(self):
        with open('./date_override.txt', encoding='utf8') as f:
            self._date_overrides = self.parse_overrides(f.readlines())
        for filename in os.listdir('./lines'):
            with open(os.path.join('./lines', filename), encoding='utf8') as f:
                l = self.parse_line(f.readlines())
                l.date_overrides = self._date_overrides
                self._lines[l.id] = l
        with open('group_def.txt', encoding='utf8') as f:
            for line in f.readlines():
                if line:
                    line = line.replace('\n', '')
                    group, description = line.split(':')
                    self._groups[group] = description

    @staticmethod
    def parse_overrides(lines: list) -> dict:
        result = dict()
        lines = [l.replace('\n', '') for l in lines if l and '\n' != l and not l.startswith('#')]
        for l in lines:
            t_str, day = l.split(' ', 1)
            day = int(day)
            result[t_str] = day
        return result

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
        except (AssertionError, IndexError):
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

    def get_all_lines_next(self, ts: float):
        """
        get next bus on all groups of lines
        in-group priority: latest > miss_last > not_today

        :param ts: timestamp
        :return: dict
        """
        results = dict()
        for line in self._lines.values():
            r = line.get_next(ts)
            if results.get(line.group) is not None:

                if results[line.group][0] == QueryStatus.NOT_TODAY:
                    # every result can override NOT_TODAY
                    results[line.group] = [r, line.id]
                elif results[line.group][0] == QueryStatus.MISS_LAST:
                    # if result is not NOT_TODAY, every result can override MISS_LAST
                    if r != QueryStatus.NOT_TODAY:
                        results[line.group] = [r, line.id]
                else:
                    # if is a time result, take the latest (the earlier)
                    if results[line.group][0] > r >= 0:
                        results[line.group] = [r, line.id]
            else:
                results[line.group] = [r, line.id]
        return results

    def get_all_lines_current(self, ts: float):
        """
        get current en route bus on all groups of lines
        in-group priority: latest > before_first > not_today

        :param ts: timestamp
        :return: dict
        """
        results = dict()
        for line in self._lines.values():
            r = line.get_current_en_route(ts)
            if results.get(line.group) is not None:

                if results[line.group][0] == QueryStatus.NOT_TODAY:
                    # every result can override NOT_TODAY
                    results[line.group] = [r, line.id]
                elif results[line.group][0] == QueryStatus.BEFORE_FIRST:
                    # if result is not NOT_TODAY, every result can override BEFORE_FIRST
                    if r != QueryStatus.NOT_TODAY:
                        results[line.group] = [r, line.id]
                else:
                    # if is a time result, take the latest (the later)
                    if results[line.group][0] < r:
                        results[line.group] = [r, line.id]
            else:
                results[line.group] = [r, line.id]
        return results

    def get_line(self, line_id) -> BusLine or None:
        return self._lines.get(line_id)

    def get_all_lines_brief(self) -> dict:
        result = dict()
        for _id, line in self._lines.items():
            result[_id] = line.name
        return result

    def get_all_lines_id(self):
        return list(self._lines.keys())

    def get_group_def(self, group_id) -> str or None:
        return self._groups.get(group_id)
