import unittest
import yaml

from nrt_logging.log_format import LogDateFormat
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager, NrtLoggerManager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum, ManualDepthEnum
from tests.test_nrt_logging.test_base import \
    NAME_1, stdout_redirect, r_stdout, TestBase

TEST_FILE_NAME = 'logger_line_style_test.py'


class NrtLoggerManagerTests(TestBase):

    def setUp(self):
        logger_1 = logger_manager.get_logger(NAME_1)
        logger_1.close_stream_handlers()

    @stdout_redirect
    def test_logger_line(self):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        msg = 'abc'
        logger.trace(msg)
        so = r_stdout.getvalue()

        log_list = yaml.safe_load(so)

        self.assertEqual(len(log_list), 1)
        log_line = log_list[0]['log']

        self._verify_log_line(
            log_line,
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.TRACE,
            f'{TEST_FILE_NAME}.{self.__class__.__name__}',
            'test_logger_line',
            29,
            msg)

    @stdout_redirect
    def test_logger_line_manual_depth(self):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        msg = 'abc'
        logger.warn(msg, ManualDepthEnum.INCREASE)

        child_msg_1 = 'child_msg_1'
        logger.error(child_msg_1, ManualDepthEnum.INCREASE)

        child_msg_2 = 'child_msg_2'
        logger.critical(child_msg_2)

        child_msg_3 = 'child_msg_3'
        logger.warn(child_msg_3, ManualDepthEnum.INCREASE)

        logger.info(child_msg_2, ManualDepthEnum.DECREASE)

        so = r_stdout.getvalue()

        expected_path = f'{TEST_FILE_NAME}.{self.__class__.__name__}'
        expected_method_name = 'test_logger_line_manual_depth'

        log_list = yaml.safe_load(so)
        self.assertEqual(1, len(log_list))
        log_dict = log_list[0]

        self._verify_log_line(
            log_dict.get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_path,
            expected_method_name,
            54,
            msg)

        children = log_dict.get('children')
        self.assertIsNotNone(children)
        self.assertEqual(3, len(children))

        self._verify_log_line(
            children[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_path,
            expected_method_name,
            57,
            child_msg_1)

        self._verify_log_line(
            children[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.CRITICAL,
            expected_path,
            expected_method_name,
            60,
            child_msg_2)

        children_2 = children[1].get('children')
        self.assertIsNotNone(children_2)
        self.assertEqual(1, len(children_2))

        self._verify_log_line(
            children_2[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_path,
            expected_method_name,
            63,
            child_msg_3)

        self._verify_log_line(
            children[2].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_path,
            expected_method_name,
            65,
            child_msg_2)

    @stdout_redirect
    def test_logger_line_multiline_message(self):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        msg = '\nabc\nqwer'
        logger.warn(msg, ManualDepthEnum.INCREASE)

        child_msg_1 = 'child_msg_1\nqwer\n\nq\n'
        logger.error(child_msg_1, ManualDepthEnum.INCREASE)

        so = r_stdout.getvalue()

        expected_path = f'{TEST_FILE_NAME}.{self.__class__.__name__}'
        expected_method_name = 'test_logger_line_multiline_message'

        log_list = yaml.safe_load(so)
        self.assertEqual(1, len(log_list))
        log_dict = log_list[0]

        self._verify_log_line(
            log_dict.get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_path,
            expected_method_name,
            137,
            msg)

        children = log_dict.get('children')
        self.assertIsNotNone(children)
        self.assertEqual(1, len(children))

        self._verify_log_line(
            children[0].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.ERROR,
            expected_path,
            expected_method_name,
            140,
            child_msg_1)

    @stdout_redirect
    def test_close_logger(self):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        msg = 'abc'
        logger.info(msg)
        so = r_stdout.getvalue()
        self.assertTrue(so)

        logger_manager.close_logger(NAME_1)

        with self.assertRaises(RuntimeError) as e:
            logger.info('a123')

        self.assertTrue('Unable write to logs' in str(e.exception))

    def test_init_logger_manager_negative(self):
        with self.assertRaises(RuntimeError) as e:
            NrtLoggerManager()

        self.assertTrue(
            'NrtLoggerManager should not be initiated' in str(e.exception))


if __name__ == '__main__':
    unittest.main()
