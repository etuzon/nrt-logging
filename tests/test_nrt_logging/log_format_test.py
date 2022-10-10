import unittest

from nrt_logging.log_format import LogElementEnum, LogFormat


class LogElementEnumTests(unittest.TestCase):
    def test_str(self):
        self.assertTrue(str(LogElementEnum.MESSAGE) == 'message')


class LogFormatTests(unittest.TestCase):
    UPDATED_DATE_FORMAT = '%Y-%m-%d'

    def test_01_get_default_date_format(self):
        self.assertTrue(
            LogFormat().date_format == LogFormat.DEFAULT_DATE_FORMAT)

    def test_02_set_date_format(self):
        log_format = LogFormat()
        log_format.date_format = self.UPDATED_DATE_FORMAT
        self.assertTrue(log_format.date_format == self.UPDATED_DATE_FORMAT)
        self.assertTrue(
            LogFormat().date_format == LogFormat.DEFAULT_DATE_FORMAT)

    def test_03_cls_set_date_format(self):
        LogFormat.set_date_format(self.UPDATED_DATE_FORMAT)
        self.assertTrue(LogFormat().date_format == self.UPDATED_DATE_FORMAT)
        LogFormat.set_date_format(LogFormat.DEFAULT_DATE_FORMAT)
        self.assertTrue(
            LogFormat().date_format == LogFormat.DEFAULT_DATE_FORMAT)


if __name__ == '__main__':
    unittest.main()
