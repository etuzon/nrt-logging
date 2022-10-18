import os
import unittest
import yaml

from nrt_logging.log_format import LogFormat
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    LogStyleEnum, FileStreamHandler, ManualDepthEnum
from tests.test_nrt_logging.test_base import \
    NAME_2, TestBase


class FileStreamHandlerTests(TestBase):
    FILE_NAME = 'log_test.log'
    PATH = os.path.join(os.getcwd(), 'temp')
    FILE_PATH = os.path.join(PATH, FILE_NAME)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.PATH):
            os.makedirs(cls.PATH)

    def setUp(self):
        if os.path.exists(self.FILE_PATH):
            os.remove(self.FILE_PATH)

    def tearDown(self):
        os.remove(self.FILE_PATH)

    def test_write_to_log(self):
        sh = FileStreamHandler(self.FILE_PATH)
        sh.log_style = LogStyleEnum.LINE
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

        f = open(self.FILE_PATH)
        log_list = yaml.safe_load(f.read())
        f.close()

        self.assertEqual(len(log_list), 4)

        expected_class_path = \
            f'logger_stream_handlers_test.py.{self.__class__.__name__}'
        expected_method_name = 'test_write_to_log'

        self._verify_log_line(
            log_list[0].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.CRITICAL,
            expected_class_path,
            expected_method_name,
            41,
            msg_1)

        children = log_list[0].get('children')
        self.assertIsNotNone(children)
        self.assertEqual(len(children), 2)

        self._verify_log_line(
            children[0].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_class_path,
            expected_method_name,
            42,
            child_1)

        self._verify_log_line(
            children[1].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_class_path,
            expected_method_name,
            43,
            child_2)

        self._verify_log_line(
            log_list[1].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            44,
            child_1)

        self._verify_log_line(
            log_list[2].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            46,
            msg_2)

        children = log_list[2].get('children')
        self.assertIsNotNone(children)
        self.assertEqual(len(children), 1)

        self._verify_log_line(
            children[0].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_class_path,
            expected_method_name,
            48,
            child_1)

        self._verify_log_line(
            log_list[3].get('log'),
            LogFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            50,
            msg_2)


if __name__ == '__main__':
    unittest.main()
