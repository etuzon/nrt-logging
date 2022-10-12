import unittest

from nrt_logging.log_format import LogElementEnum, LogFormat


class LogElementEnumTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual(LogElementEnum.MESSAGE.name, 'message')

    def test_line_format(self):
        self.assertEqual(LogElementEnum.DATE.name, '$date$')

    def test_str(self):
        self.assertEqual(str(LogElementEnum.MESSAGE), 'message')


class LogFormatTests(unittest.TestCase):
    UPDATED_DATE_FORMAT = '%Y-%m-%d'
    UPDATED_YAML_ELEMENTS = {LogElementEnum.LOG_LEVEL, LogElementEnum.PATH}

    def test_get_default_date_format(self):
        self.assertEqual(
            LogFormat().date_format, LogFormat.DEFAULT_DATE_FORMAT)

    def test_set_date_format(self):
        log_format = LogFormat()
        log_format.date_format = self.UPDATED_DATE_FORMAT
        self.assertEqual(log_format.date_format, self.UPDATED_DATE_FORMAT)
        self.assertEqual(
            LogFormat().date_format, LogFormat.DEFAULT_DATE_FORMAT)

    def test_cls_set_date_format(self):
        LogFormat.set_date_format(self.UPDATED_DATE_FORMAT)
        self.assertEqual(LogFormat().date_format, self.UPDATED_DATE_FORMAT)
        LogFormat.set_date_format(LogFormat.DEFAULT_DATE_FORMAT)
        self.assertEqual(
            LogFormat().date_format, LogFormat.DEFAULT_DATE_FORMAT)

    def test_set_yaml_elements(self):
        log_format = LogFormat()
        log_format.yaml_elements = self.UPDATED_YAML_ELEMENTS
        self.assertEqual(log_format.yaml_elements, self.UPDATED_YAML_ELEMENTS)
        self.assertEqual(
            LogFormat().yaml_elements, LogFormat.DEFAULT_YAML_ELEMENTS)

    def test_cls_set_yaml_elements(self):
        LogFormat.set_yaml_elements(self.UPDATED_YAML_ELEMENTS)
        self.assertEqual(
            LogFormat().yaml_elements, self.UPDATED_YAML_ELEMENTS)
        LogFormat.set_yaml_elements(LogFormat.DEFAULT_YAML_ELEMENTS)
        self.assertEqual(
            LogFormat().yaml_elements, LogFormat.DEFAULT_YAML_ELEMENTS)


if __name__ == '__main__':
    unittest.main()
