import datetime
from unittest import TestCase

from utils import BusSchedule, QueryStatus

sched = BusSchedule()


class TestBusSchedule(TestCase):
    def test_read_line_info(self):
        self.assertEqual(sorted(sched.get_all_lines_id()), sorted(['line1-1', 'line1-1-peak', 'line1-1-weekend',
                                                                   'line1-2', 'line1-2-peak', 'line1-2-weekend',
                                                                   'line2-1', 'line2-1-weekend',
                                                                   'line2-2', 'line2-2-weekend']))

    def test_parse_overrides(self):
        self.assertDictEqual(sched.parse_overrides(['\n', '2018-01-01 4\n', '2017-12-01 6', '\n']),
                             {'2018-01-01': 4, '2017-12-01': 6})

    def test_parse_line(self):
        with self.assertRaises(ValueError):
            sched.parse_line([''])

    def test_get_all_lines_next(self):
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 4, 25, 16, 46, 44, 139715).timestamp()),
                             {'line1-1': [1700, 'line1-1'],
                              'line1-2': [1700, 'line1-2'],
                              'line2-1': [1840, 'line2-1'],
                              'line2-2': [QueryStatus.MISS_LAST, 'line2-2']
                              })
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 4, 25, 23, 46, 44, 139715).timestamp()),
                             {'line1-1': [QueryStatus.MISS_LAST, 'line1-1-peak'],
                              'line1-2': [QueryStatus.MISS_LAST, 'line1-2-peak'],
                              'line2-1': [QueryStatus.MISS_LAST, 'line2-1'],
                              'line2-2': [QueryStatus.MISS_LAST, 'line2-2']
                              })
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 4, 22, 23, 46, 44, 139715).timestamp()),
                             {'line1-1': [QueryStatus.MISS_LAST, 'line1-1-weekend'],
                              'line1-2': [QueryStatus.MISS_LAST, 'line1-2-weekend'],
                              'line2-1': [QueryStatus.MISS_LAST, 'line2-1-weekend'],
                              'line2-2': [QueryStatus.MISS_LAST, 'line2-2-weekend']
                              })
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 4, 28, 16, 46, 44, 139715).timestamp()),
                             {'line1-1': [1700, 'line1-1'],
                              'line1-2': [1700, 'line1-2'],
                              'line2-1': [1840, 'line2-1'],
                              'line2-2': [QueryStatus.MISS_LAST, 'line2-2']
                              })
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 12, 2, 16, 46, 44, 139715).timestamp()),
                             {'line1-1': [QueryStatus.NOT_TODAY, 'line1-1-weekend'],
                              'line1-2': [QueryStatus.NOT_TODAY, 'line1-2-weekend'],
                              'line2-1': [QueryStatus.NOT_TODAY, 'line2-1-weekend'],
                              'line2-2': [QueryStatus.NOT_TODAY, 'line2-2-weekend']
                              })

    def test_get_all_lines_current(self):
        self.assertDictEqual(
            sched.get_all_lines_current(datetime.datetime(2018, 4, 25, 16, 46, 44, 139715).timestamp()),
            {'line1-1': [1640, 'line1-1'],
             'line1-2': [1640, 'line1-2'],
             'line2-1': [1240, 'line2-1'],
             'line2-2': [1330, 'line2-2']
             })
        self.assertDictEqual(
            sched.get_all_lines_current(datetime.datetime(2018, 4, 25, 23, 46, 44, 139715).timestamp()),
            {'line1-1': [2100, 'line1-1'],
             'line1-2': [2200, 'line1-2'],
             'line2-1': [2220, 'line2-1'],
             'line2-2': [1330, 'line2-2']
             })
        self.assertDictEqual(
            sched.get_all_lines_current(datetime.datetime(2018, 4, 22, 23, 46, 44, 139715).timestamp()),
            {'line1-1': [2100, 'line1-1-weekend'],
             'line1-2': [2200, 'line1-2-weekend'],
             'line2-1': [2230, 'line2-1-weekend'],
             'line2-2': [1520, 'line2-2-weekend']
             })
        self.assertDictEqual(
            sched.get_all_lines_current(datetime.datetime(2018, 4, 28, 16, 46, 44, 139715).timestamp()),
            {'line1-1': [1640, 'line1-1'],
             'line1-2': [1640, 'line1-2'],
             'line2-1': [1240, 'line2-1'],
             'line2-2': [1330, 'line2-2']
             })
        self.assertDictEqual(sched.get_all_lines_next(datetime.datetime(2018, 12, 2, 16, 46, 44, 139715).timestamp()),
                             {'line1-1': [QueryStatus.NOT_TODAY, 'line1-1-weekend'],
                              'line1-2': [QueryStatus.NOT_TODAY, 'line1-2-weekend'],
                              'line2-1': [QueryStatus.NOT_TODAY, 'line2-1-weekend'],
                              'line2-2': [QueryStatus.NOT_TODAY, 'line2-2-weekend']
                              })

    def test_get_all_lines_brief(self):
        self.assertDictEqual(sched.get_all_lines_brief(),
                             {'line1-1': '工作日非高峰期 欣园-科研楼',
                              'line1-1-peak': '工作日高峰期 欣园-科研楼',
                              'line1-1-weekend': '节假日 欣园-科研楼',
                              'line1-2': '工作日非高峰期 科研楼-欣园',
                              'line1-2-peak': '工作日高峰期 科研楼-欣园',
                              'line1-2-weekend': '节假日 科研楼-欣园',
                              'line2-1': '工作日 荔园-集悦城',
                              'line2-1-weekend': '节假日 荔园-集悦城',
                              'line2-2': '工作日 集悦城-荔园',
                              'line2-2-weekend': '节假日 集悦城-荔园'
                              })

    def test_get_group_def(self):
        self.assertEqual(sched.get_group_def('line1-1'), '欣园-科研楼平峰线')
        self.assertEqual(sched.get_group_def('line1-1-peak'), '欣园-科研楼高峰线')
        self.assertEqual(sched.get_group_def('line2-1'), '荔园-集悦城')
        self.assertEqual(sched.get_group_def('line2-2'), '集悦城-荔园')
