from unittest import TestCase
from utils import BusLine, QueryStatus


class TestBusLine(TestCase):
    def test_bin_search(self):
        tl = [800, 820, 840, 900, 920, 940, 1020, 1040, 1100, 1120, 1140, 1300, 1320, 1400, 1420, 1440, 1500, 1520,
              1540, 1620, 1640, 1700, 1720, 1740, 1800, 1820, 1840, 1900, 2000, 2100]
        self.assertEqual(BusLine.bin_search(tl, 1506), 1520)
        self.assertEqual(BusLine.bin_search(tl, 700), 800)
        self.assertEqual(BusLine.bin_search(tl, 800), 820)
        self.assertEqual(BusLine.bin_search(tl, 1401), 1420)

    def test_get_next(self):
        r = {
            'id': 'testLine1',
            'name': '测试线路1',
            'day': [1, 2, 3, 4, 5],
            'route': '站点1->站点2',
            'time_list': [800, 820, 840, 900, 920, 940, 1020, 1040, 1100, 1120, 1140, 1300, 1320, 1400, 1420, 1440,
                          1500, 1520, 1540, 1620, 1640, 1700, 1720, 1740, 1800, 1820, 1840, 1900, 2000, 2100]
        }
        bl = BusLine(**r)
        self.assertEqual(bl.get_next(1524213679), 1700)
        self.assertEqual(bl.get_next(1524213600), 1700)

        self.assertEqual(bl.get_next(1524300079), QueryStatus.NOT_TODAY)
        self.assertEqual(bl.get_next(1524235200), QueryStatus.MISS_LAST)
