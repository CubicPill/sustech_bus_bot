import datetime
from unittest import TestCase

from utils import BusLine, QueryStatus

r = {
    'id': 'testLine1',
    'name': '测试线路1',
    'group': 'testgroup',
    'day': [1, 2, 3, 4, 5],
    'route': '站点1->站点2',
    'time_list': [800, 820, 840, 900, 920, 940, 1020, 1040, 1100, 1120, 1140, 1300, 1320, 1400, 1420, 1440,
                  1500, 1520, 1540, 1620, 1640, 1700, 1720, 1740, 1800, 1820, 1840, 1900, 2000, 2100]
}
bl = BusLine(**r)


class TestBusLine(TestCase):
    def test_bin_search(self):
        tl = [800, 820, 840, 900, 920, 940, 1020, 1040, 1100, 1120, 1140, 1300, 1320, 1400, 1420, 1440, 1500, 1520,
              1540, 1620, 1640, 1700, 1720, 1740, 1800, 1820, 1840, 1900, 2000, 2100]
        self.assertEqual(BusLine.bin_search(tl, 1506), tl.index(1520))
        self.assertEqual(BusLine.bin_search(tl, 700), tl.index(800))
        self.assertEqual(BusLine.bin_search(tl, 800), tl.index(820))
        self.assertEqual(BusLine.bin_search(tl, 1401), tl.index(1420))

    def test_get_next(self):
        self.assertEqual(bl.get_next(datetime.datetime(2018, 4, 20, 16, 46, 44, 139715).timestamp()), 1700)
        self.assertEqual(bl.get_next(datetime.datetime(2018, 4, 20, 16, 40, 0, 0).timestamp()), 1700)
        self.assertEqual(bl.get_next(datetime.datetime(2018, 4, 21, 16, 46, 44, 139715).timestamp()),
                         QueryStatus.NOT_TODAY)
        self.assertEqual(bl.get_next(datetime.datetime(2018, 4, 20, 21, 46, 44, 139715).timestamp()),
                         QueryStatus.MISS_LAST)

    def test_get_current(self):
        self.assertEqual(bl.get_current_en_route(datetime.datetime(2018, 4, 20, 16, 46, 44, 139715).timestamp()), 1640)
        self.assertEqual(bl.get_current_en_route(datetime.datetime(2018, 4, 20, 16, 40, 0, 0).timestamp()), 1640)
        self.assertEqual(bl.get_current_en_route(datetime.datetime(2018, 4, 21, 16, 46, 44, 139715).timestamp()),
                         QueryStatus.NOT_TODAY)
        self.assertEqual(bl.get_current_en_route(datetime.datetime(2018, 4, 20, 1, 46, 44, 139715).timestamp()),
                         QueryStatus.BEFORE_FIRST)

    def test_time_to_string(self):
        self.assertEqual(BusLine.time_to_string(1230), '12:30')
        self.assertEqual(BusLine.time_to_string(0), '0:00')
        self.assertEqual(BusLine.time_to_string(100), '1:00')
        self.assertEqual(BusLine.time_to_string(1), '0:01')

    def test_to_string(self):
        self.assertEqual(bl.to_string(), '\n'.join(['ID: testLine1',
                                                    '名称: 测试线路1',
                                                    '分组: testgroup',
                                                    '运行时间: 周一, 周二, 周三, 周四, 周五',
                                                    '路线: 站点1->站点2',
                                                    '发车时刻: 8:00, 8:20, 8:40, 9:00, 9:20, 9:40, 10:20, 10:40, 11:00, '
                                                    '11:20, 11:40, 13:00, 13:20, 14:00, 14:20, 14:40, 15:00, 15:20, '
                                                    '15:40, 16:20, 16:40, 17:00, 17:20, 17:40, 18:00, 18:20, 18:40, '
                                                    '19:00, 20:00, 21:00']))

    def test_get_day_in_week(self):
        self.assertEqual(bl.get_day_in_week(datetime.datetime(2018, 4, 20, 16, 46, 44, 139715).timestamp()), 5)
        self.assertEqual(bl.get_day_in_week(datetime.datetime(2018, 4, 21, 16, 46, 44, 139715).timestamp()), 6)
        self.assertEqual(bl.get_day_in_week(datetime.datetime(2018, 4, 22, 16, 46, 44, 139715).timestamp()), 7)
        bl.add_override_date('2018-04-22', 4)
        self.assertEqual(bl.get_day_in_week(datetime.datetime(2018, 4, 22, 16, 46, 44, 139715).timestamp()), 4)
        bl.add_override_date('2018-04-22', 0)
        self.assertEqual(bl.get_day_in_week(datetime.datetime(2018, 4, 22, 16, 46, 44, 139715).timestamp()), 0)

    def test_override_all(self):
        bl.add_override_date('2019-01-14', 0)
        self.assertEqual(bl.get_next(datetime.datetime(2019, 1, 14, 21, 46, 44, 139715).timestamp()),
                         QueryStatus.NOT_TODAY)
