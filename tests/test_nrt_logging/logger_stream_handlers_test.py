import os
import unittest
import yaml

from nrt_logging.log_format import LogDateFormat
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    LogStyleEnum, FileStreamHandler, ManualDepthEnum
from tests.test_nrt_logging.test_base import \
    NAME_2, TestBase


class LogStyleEnumTests(TestBase):

    def test_name(self):
        self.assertEqual('yaml', LogStyleEnum.YAML.name)

    def test_build_by_name(self):
        self.assertEqual(
            LogStyleEnum.YAML, LogStyleEnum.build_by_name('YaMl'))

    def test_build_by_name_not_exist_negative(self):
        with self.assertRaises(ValueError):
            LogStyleEnum.build_by_name('not exist')

    def test_build_by_value(self):
        self.assertEqual(LogStyleEnum.LINE, LogStyleEnum.build_by_value(2))

    def test_build_by_value_not_exist_negative(self):
        with self.assertRaises(ValueError):
            LogStyleEnum.build_by_value(999)


class FileStreamHandlerTests(TestBase):
    FILE_NAME = 'log_test.log'
    FILE_PATH = os.path.join(TestBase.TEMP_PATH, FILE_NAME)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.TEMP_PATH):
            os.makedirs(cls.TEMP_PATH)

    def setUp(self):
        if os.path.exists(self.FILE_PATH):
            os.remove(self.FILE_PATH)

    def tearDown(self):
        os.remove(self.FILE_PATH)

    def test_write_to_log(self):
        sh = FileStreamHandler(self.FILE_PATH)
        sh.style = LogStyleEnum.LINE
        logger = logger_manager.get_logger(NAME_2)
        logger.add_stream_handler(sh)
        msg_1 = 'asdf'
        msg_2 = 'qwer'
        child_1 = '1234'
        child_2 = '56789'

        logger.critical(msg_1, ManualDepthEnum.INCREASE)
        logger.error(child_1, ManualDepthEnum.INCREASE)
        logger.warn(child_2)
        logger.info(child_1, ManualDepthEnum.DECREASE)
        logger.debug(child_2, ManualDepthEnum.DECREASE)
        logger.info(msg_2, ManualDepthEnum.DECREASE)
        logger.increase_depth()
        logger.error(child_1)
        logger.decrease_depth()
        logger.info(msg_2)

        with open(self.FILE_PATH) as f:
            log_list = yaml.safe_load(f.read())

        self.assertEqual(4, len(log_list))

        expected_class_path = \
            f'logger_stream_handlers_test.py.{self.__class__.__name__}'
        expected_method_name = 'test_write_to_log'

        self._verify_log_line(
            log_list[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.CRITICAL,
            expected_class_path,
            expected_method_name,
            61,
            msg_1)

        children = log_list[0].get('children')
        self.assertIsNotNone(children)
        self.assertEqual(2, len(children))

        self._verify_log_line(
            children[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_class_path,
            expected_method_name,
            62,
            child_1)

        self._verify_log_line(
            children[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_class_path,
            expected_method_name,
            63,
            child_2)

        self._verify_log_line(
            log_list[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            64,
            child_1)

        self._verify_log_line(
            log_list[2].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            66,
            msg_2)

        children = log_list[2].get('children')
        self.assertIsNotNone(children)
        self.assertEqual(1, len(children))

        self._verify_log_line(
            children[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_class_path,
            expected_method_name,
            68,
            child_1)

        self._verify_log_line(
            log_list[3].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            70,
            msg_2)


if __name__ == '__main__':
    unittest.main()
