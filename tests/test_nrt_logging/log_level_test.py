import unittest

from nrt_logging.log_level import LogLevelEnum


class LogLevelEnumTests(unittest.TestCase):

    def test_name(self):
        self.assertTrue(LogLevelEnum.DEBUG.name == 'DEBUG')

    def test_str(self):
        self.assertTrue(str(LogLevelEnum.INFO) == 'INFO')
        self.assertTrue(f'{LogLevelEnum.ERROR}' == 'ERROR')

    def test_eq(self):
        self.assertEqual(LogLevelEnum.CRITICAL, LogLevelEnum.CRITICAL)
        self.assertTrue(LogLevelEnum.DEBUG == LogLevelEnum.DEBUG)

    def test_eq_negative(self):
        self.assertFalse(LogLevelEnum.INFO == LogLevelEnum.DEBUG)

    def test_qt(self):
        self.assertTrue(LogLevelEnum.CRITICAL > LogLevelEnum.WARN)

    def test_qt_negative(self):
        self.assertFalse(LogLevelEnum.INFO > LogLevelEnum.WARN)

    def test_qe(self):
        self.assertTrue(LogLevelEnum.CRITICAL >= LogLevelEnum.WARN)
        self.assertTrue(LogLevelEnum.WARN >= LogLevelEnum.WARN)

    def test_qe_negative(self):
        self.assertFalse(LogLevelEnum.INFO >= LogLevelEnum.ERROR)

    def test_le(self):
        self.assertTrue(LogLevelEnum.INFO <= LogLevelEnum.WARN)
        self.assertTrue(LogLevelEnum.TRACE <= LogLevelEnum.TRACE)

    def test_le_negative(self):
        self.assertFalse(LogLevelEnum.INFO <= LogLevelEnum.TRACE)

    def test_lt(self):
        self.assertTrue(LogLevelEnum.TRACE < LogLevelEnum.INFO)

    def test_lt_negative(self):
        self.assertFalse(LogLevelEnum.INFO < LogLevelEnum.TRACE)

    def test_log_level_not_exist_negative(self):
        with self.assertRaises(ValueError):
            LogLevelEnum.build('not exist')


if __name__ == '__main__':
    unittest.main()
