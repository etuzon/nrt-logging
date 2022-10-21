import unittest

from nrt_logging.log_format import LogElementEnum, LogYamlElements


class LogElementEnumTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual('message', LogElementEnum.MESSAGE.name)

    def test_line_format(self):
        self.assertEqual('$date$', LogElementEnum.DATE.line_format)

    def test_str(self):
        self.assertEqual('message', str(LogElementEnum.MESSAGE))


class LogYamlElementsTests(unittest.TestCase):
    UPDATED_YAML_ELEMENTS = {LogElementEnum.LOG_LEVEL, LogElementEnum.PATH}

    def test_set_yaml_elements(self):
        log_yaml_elements = LogYamlElements()
        log_yaml_elements.yaml_elements = self.UPDATED_YAML_ELEMENTS
        self.assertEqual(
            self.UPDATED_YAML_ELEMENTS, log_yaml_elements.yaml_elements)
        self.assertEqual(
            LogYamlElements.DEFAULT_YAML_ELEMENTS,
            LogYamlElements().yaml_elements)


if __name__ == '__main__':
    unittest.main()
