import unittest

from parameterized import parameterized

from nrt_logging.log_format import LogElementEnum, LogYamlElements


class LogElementEnumTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual('message', LogElementEnum.MESSAGE.name)

    def test_line_format(self):
        self.assertEqual('$date$', LogElementEnum.DATE.line_format)

    def test_str(self):
        self.assertEqual('message', str(LogElementEnum.MESSAGE))

    def test_element_not_exist_negative(self):
        with self.assertRaises(ValueError):
            LogElementEnum.build('not exist')


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

    @parameterized.expand([
        [{LogElementEnum.DATE, LogElementEnum.LOG_LEVEL}],
        [[LogElementEnum.DATE, LogElementEnum.LOG_LEVEL]]
    ])
    def test_build(self, log_yaml_elements):
        self.assertEqual(
            {LogElementEnum.DATE, LogElementEnum.LOG_LEVEL},
            LogYamlElements.build(log_yaml_elements).yaml_elements)


if __name__ == '__main__':
    unittest.main()
