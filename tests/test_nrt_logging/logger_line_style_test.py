import os
import unittest
import yaml

from nrt_logging.log_format import LogDateFormat
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager, NrtLoggerManager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum, ManualDepthEnum, FileStreamHandler
from tests.test_nrt_logging.test_base import \
    NAME_1, stdout_redirect, r_stdout, TestBase, NAME_2

TEST_FILE_NAME = 'logger_line_style_test.py'


class NrtLoggerManagerTests(TestBase):
    FILE_NAME_1 = 'log_line_test_1.txt'
    FILE_PATH_1 = os.path.join(TestBase.TEMP_PATH, FILE_NAME_1)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.TEMP_PATH):
            os.makedirs(cls.TEMP_PATH)

    def setUp(self):
        self.__clean_setup()

    def tearDown(self):
        self.__clean_setup()

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

        self.assertEqual(1, len(log_list))
        log_line = log_list[0]['log']

        self._verify_log_line(
            log_line,
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.TRACE,
            f'{TEST_FILE_NAME}.{self.__class__.__name__}',
            'test_logger_line',
            39,
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
            64,
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
            67,
            child_msg_1)

        self._verify_log_line(
            children[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.CRITICAL,
            expected_path,
            expected_method_name,
            70,
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
            73,
            child_msg_3)

        self._verify_log_line(
            children[2].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_path,
            expected_method_name,
            75,
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
            147,
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
            150,
            child_msg_1)

    @stdout_redirect
    def test_default_sh_parameters(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        msg = 'abcd'
        logger.info(msg)

        so = r_stdout.getvalue()

        log_list = yaml.safe_load(so)

        self.assertEqual(len(log_list), 1)
        log_line = log_list[0]['log']

        self._verify_log_line(
            log_line,
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            f'{TEST_FILE_NAME}.{self.__class__.__name__}',
            'test_default_sh_parameters',
            190,
            msg)

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

    @stdout_redirect
    def test_logger_log_print_less_log_level_negative(self):
        sh = ConsoleStreamHandler()
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        msg = 'abcd'

        logger.log_level = LogLevelEnum.DEBUG
        logger.trace(msg)
        self.assertFalse(bool(r_stdout.getvalue()))

        logger.log_level = LogLevelEnum.INFO
        logger.debug(msg)
        self.assertFalse(bool(r_stdout.getvalue()))

        logger.update_log_level(
            LogLevelEnum.WARN, is_update_sh=False)
        logger.info(msg)
        self.assertFalse(bool(r_stdout.getvalue()))

        logger.log_level = LogLevelEnum.ERROR
        logger.warn(msg)
        self.assertFalse(bool(r_stdout.getvalue()))

        logger.log_level = LogLevelEnum.CRITICAL
        logger.error(msg)
        self.assertFalse(bool(r_stdout.getvalue()))

    @stdout_redirect
    def test_add_stream_handler_with_is_min_sh_logger_level_false(self):
        c_sh = ConsoleStreamHandler()
        c_sh.log_level = LogLevelEnum.INFO
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(c_sh)

        f_sh = FileStreamHandler(self.FILE_PATH_1)
        f_sh.log_level = LogLevelEnum.DEBUG
        logger.add_stream_handler(f_sh, is_min_sh_logger_level=False)

        msg_1 = 'abcd'
        msg_2 = 'efgh'

        logger.debug(msg_1)
        logger.error(msg_2)

        so = r_stdout.getvalue()
        log_list = yaml.safe_load(so)

        self.assertEqual(1, len(log_list))

        with open(self.FILE_PATH_1) as f:
            file_log_list = yaml.safe_load(f.read())

        self.assertEqual(1, len(file_log_list))

    @stdout_redirect
    def test_update_log_level(self):
        c_sh = ConsoleStreamHandler()
        c_sh.log_level = LogLevelEnum.DEBUG
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(c_sh, is_min_sh_logger_level=False)

        msg_1 = 'abcd'

        logger.debug(msg_1)

        so = r_stdout.getvalue()
        self.assertFalse(bool(so))

        logger.update_log_level(
            LogLevelEnum.DEBUG, is_update_sh=True)

        logger.debug(msg_1)

        so = r_stdout.getvalue()
        log_list = yaml.safe_load(so)

        self.assertEqual(1, len(log_list))

    @stdout_redirect
    def test_same_sh_in_multiple_loggers(self):
        msg_1 = 'msg_1'
        msg_2 = 'msg_2'
        msg_3 = 'msg_3'

        c_sh = ConsoleStreamHandler()
        c_sh.log_level = LogLevelEnum.DEBUG
        c_sh.set_log_style(LogStyleEnum.LINE)
        c_sh.log_line_template = 'Test $log_level$ $message$'

        logger_1 = logger_manager.get_logger(NAME_1)
        logger_2 = logger_manager.get_logger(NAME_2)

        logger_1.log_level = LogLevelEnum.INFO
        logger_2.log_level = LogLevelEnum.DEBUG

        logger_1.add_stream_handler(c_sh, is_min_sh_logger_level=False)
        logger_2.add_stream_handler(c_sh, is_min_sh_logger_level=False)

        logger_1.info(msg_1)
        logger_1.debug(msg_2)
        logger_2.debug(msg_3)

        console_log_list = yaml.safe_load(r_stdout.getvalue())

        self.assertEqual(2, len(console_log_list))

        self.assertTrue(LogLevelEnum.INFO.name in console_log_list[0]['log'])
        self.assertTrue(msg_1 in console_log_list[0]['log'])

        self.assertTrue(LogLevelEnum.DEBUG.name in console_log_list[1]['log'])
        self.assertTrue(msg_3 in console_log_list[1]['log'])

    def __clean_setup(self):
        if os.path.exists(self.FILE_PATH_1):
            os.remove(self.FILE_PATH_1)

        logger_manager.close_logger(NAME_1)
        logger_manager.close_logger(NAME_2)


if __name__ == '__main__':
    unittest.main()
