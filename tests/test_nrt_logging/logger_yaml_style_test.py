import sys
import unittest
from deepdiff import DeepDiff
from io import StringIO
from typing import Optional
import yaml
from nrt_logging.log_format import LogElementEnum
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import logger_manager, NrtLogger
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, ManualDepthEnum, LoggerStreamHandlerBase

r_stdout: Optional[StringIO] = None


def stdout_redirect(func):

    def inner(*args, **kwargs):
        global r_stdout

        temp_stdout = sys.stdout
        sys.stdout = r_stdout = StringIO()

        func(*args, **kwargs)

        sys.stdout = temp_stdout
        r_stdout = None

    return inner


NAME_1 = 'name_1'
NAME_2 = 'name_2'


class A:
    MSG_1 = 'ddddd'
    MSG_2 = 'eeeee'
    MSG_3 = 'fffff'

    MSG_INCREASE = 'MANUAL INCREASE'
    MSG_DECREASE = 'MANUAL DECREASE'

    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def a(self):
        self.__logger.info(self.MSG_1)
        self.b()

    def b(self):
        self.__logger.warn(self.MSG_2)

    def c_manual(self):
        self.__logger.critical(self.MSG_INCREASE, ManualDepthEnum.INCREASE)
        self.b()
        self.__logger.debug(self.MSG_DECREASE, ManualDepthEnum.DECREASE)
        self.__logger.error(self.MSG_DECREASE, ManualDepthEnum.DECREASE)


class B:
    MSG_1 = 'aaaaaaa'
    MSG_2 = 'bbbbbbb'
    MSG_3 = 'ccccccc'

    MSG_INCREASE = 'MANUAL INCREASE'
    MSG_DECREASE = 'MANUAL DECREASE'

    __a: A
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__a = A()

    def a(self):
        self.__logger.info(self.MSG_1)
        self.__a.a()
        self.b()

    def b(self):
        self.__logger.warn(self.MSG_2)
        self.__a.b()

    def c_manual(self):
        self.__logger.critical(self.MSG_INCREASE, ManualDepthEnum.INCREASE)
        self.b()
        # Will not be printed as log level is INFO
        self.__logger.debug(self.MSG_INCREASE, ManualDepthEnum.INCREASE)
        self.__logger.error(self.MSG_INCREASE, ManualDepthEnum.INCREASE)
        self.__logger.info(self.MSG_DECREASE, ManualDepthEnum.DECREASE)
        self.__logger.info(self.MSG_DECREASE, ManualDepthEnum.DECREASE)

    def d_manual(self):
        self.__logger.error(self.MSG_3)
        self.__a.c_manual()
        self.__logger.info(self.MSG_3)


CA_A_LINE = 50
CA_B_LINE = 54
CB_A_LINE = 79
CB_B_LINE = 84


TEST_FILE_NAME = 'logger_yaml_style_test.py'


class NrtLoggerManagerTests(unittest.TestCase):
    def setUp(self):
        logger_1 = logger_manager.get_logger(NAME_1)
        logger_1.close_stream_handlers()

    def test_01_get_logger(self):
        self.assertTrue(
            isinstance(logger_manager.get_logger(NAME_1), NrtLogger))

    @stdout_redirect
    def test_02_logger_yaml(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        msg = 'abc'
        logger.info(msg)
        so = r_stdout.getvalue()

        expected_path = f'{TEST_FILE_NAME}.{self.__class__.__name__}'
        expected_method_name = 'test_02_logger_yaml'

        yaml_dict = yaml.safe_load(so)

        expected_yaml_dict = \
            {
                LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
                LogElementEnum.PATH.value: expected_path,
                LogElementEnum.METHOD.value: expected_method_name,
                LogElementEnum.LINE_NUMBER.value: 126,
                LogElementEnum.MESSAGE.value: msg
            }

        self.__verify_yaml_dict(yaml_dict, expected_yaml_dict)

    @stdout_redirect
    def test_03_logger_yaml_manual_depth(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        msg = 'abc'
        logger.warn(msg, ManualDepthEnum.INCREASE)
        child_msg = 'child msg'
        logger.error(child_msg, ManualDepthEnum.INCREASE)
        so = r_stdout.getvalue()

        expected_path = f'{TEST_FILE_NAME}.{self.__class__.__name__}'
        expected_method_name = 'test_03_logger_yaml_manual_depth'

        yaml_dict = yaml.safe_load(so)

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
            LogElementEnum.PATH.value: expected_path,
            LogElementEnum.METHOD.value: expected_method_name,
            LogElementEnum.LINE_NUMBER.value: 151,
            LogElementEnum.MESSAGE.value: msg,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.ERROR.name,
                    LogElementEnum.PATH.value: expected_path,
                    LogElementEnum.METHOD.value: expected_method_name,
                    LogElementEnum.LINE_NUMBER.value: 153,
                    LogElementEnum.MESSAGE.value: child_msg
                }
            ]
        }

        self.__verify_yaml_dict(yaml_dict, expected_yaml_dict)

    @stdout_redirect
    def test_04_logger_yaml_depth(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        b = B()
        b.a()
        b.b()

        so = r_stdout.getvalue()
        log_doc_list = \
            so.split(LoggerStreamHandlerBase.YAML_DOCUMENT_SEPARATOR)

        # First element is empty
        self.assertEqual(len(log_doc_list), 4)

        cb_a_ca_a_ca_b_yaml = yaml.safe_load(log_doc_list[1])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'a',
            LogElementEnum.LINE_NUMBER.value: CB_A_LINE,
            LogElementEnum.MESSAGE.value: B.MSG_1,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
                    LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.A',
                    LogElementEnum.METHOD.value: 'a',
                    LogElementEnum.LINE_NUMBER.value: CA_A_LINE,
                    LogElementEnum.MESSAGE.value: A.MSG_1,
                    'children': [
                        {
                            LogElementEnum.LOG_LEVEL.value:
                                LogLevelEnum.WARN.name,
                            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.A',
                            LogElementEnum.METHOD.value: 'b',
                            LogElementEnum.LINE_NUMBER.value: CA_B_LINE,
                            LogElementEnum.MESSAGE.value: A.MSG_2,
                        }
                    ]
                }
            ]
        }

        self.__verify_yaml_dict(
            cb_a_ca_a_ca_b_yaml, expected_yaml_dict)

        cb_b_ca_b_yaml = yaml.safe_load(log_doc_list[2])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'b',
            LogElementEnum.LINE_NUMBER.value: CB_B_LINE,
            LogElementEnum.MESSAGE.value: B.MSG_2,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
                    LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.A',
                    LogElementEnum.METHOD.value: 'b',
                    LogElementEnum.LINE_NUMBER.value: CA_B_LINE,
                    LogElementEnum.MESSAGE.value: A.MSG_2
                }
            ]
        }

        self.__verify_yaml_dict(
            cb_b_ca_b_yaml, expected_yaml_dict)

        cb_b_ca_b_yaml = yaml.safe_load(log_doc_list[3])

        self.__verify_yaml_dict(
            cb_b_ca_b_yaml, expected_yaml_dict)

    @stdout_redirect
    def test_05_logger_yaml_depth_and_manual_depth(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        b = B()
        b.c_manual()
        b.b()

        so = r_stdout.getvalue()

        log_doc_list = \
            so.split(LoggerStreamHandlerBase.YAML_DOCUMENT_SEPARATOR)

        self.assertEqual(len(log_doc_list), 5)

        cb_c_cb_b_ca_b_yaml = yaml.safe_load(log_doc_list[1])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.CRITICAL.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'c_manual',
            LogElementEnum.LINE_NUMBER.value: 88,
            LogElementEnum.MESSAGE.value: B.MSG_INCREASE,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
                    LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
                    LogElementEnum.METHOD.value: 'b',
                    LogElementEnum.LINE_NUMBER.value: CB_B_LINE,
                    LogElementEnum.MESSAGE.value: B.MSG_2,
                    'children': [
                        {
                            LogElementEnum.LOG_LEVEL.value:
                                LogLevelEnum.WARN.name,
                            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.A',
                            LogElementEnum.METHOD.value: 'b',
                            LogElementEnum.LINE_NUMBER.value: CA_B_LINE,
                            LogElementEnum.MESSAGE.value: A.MSG_2,
                        }
                    ]
                },
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.ERROR.name,
                    LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
                    LogElementEnum.METHOD.value: 'c_manual',
                    LogElementEnum.LINE_NUMBER.value: 92,
                    LogElementEnum.MESSAGE.value: B.MSG_INCREASE,
                }
            ]
        }

        self.__verify_yaml_dict(
            cb_c_cb_b_ca_b_yaml, expected_yaml_dict)

        cb_c_yaml = yaml.safe_load(log_doc_list[2])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'c_manual',
            LogElementEnum.LINE_NUMBER.value: 93,
            LogElementEnum.MESSAGE.value: B.MSG_DECREASE
        }

        self.__verify_yaml_dict(cb_c_yaml, expected_yaml_dict)

        cb_c_yaml = yaml.safe_load(log_doc_list[3])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'c_manual',
            LogElementEnum.LINE_NUMBER.value: 94,
            LogElementEnum.MESSAGE.value: B.MSG_DECREASE
        }

        self.__verify_yaml_dict(cb_c_yaml, expected_yaml_dict)

        cb_b_ca_b_yaml = yaml.safe_load(log_doc_list[4])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
            LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.B',
            LogElementEnum.METHOD.value: 'b',
            LogElementEnum.LINE_NUMBER.value: CB_B_LINE,
            LogElementEnum.MESSAGE.value: B.MSG_2,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.WARN.name,
                    LogElementEnum.PATH.value: f'{TEST_FILE_NAME}.A',
                    LogElementEnum.METHOD.value: 'b',
                    LogElementEnum.LINE_NUMBER.value: CA_B_LINE,
                    LogElementEnum.MESSAGE.value: A.MSG_2
                }
            ]
        }

        self.__verify_yaml_dict(cb_b_ca_b_yaml, expected_yaml_dict)

    @stdout_redirect
    def test_06_logger_yaml_increase_and_decrease_depth_manually(self):
        sh = ConsoleStreamHandler()
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)

        msg_1 = 'abcd'
        msg_2 = 'qwer'

        logger.info(msg_1)
        logger.increase_depth()
        logger.error(msg_2)
        logger.increase_depth()
        logger.critical(msg_1)
        logger.decrease_depth(2)
        logger.error(msg_1)

        class_path = f'{TEST_FILE_NAME}.{self.__class__.__name__}'
        method_name = \
            'test_06_logger_yaml_increase_and_decrease_depth_manually'

        so = r_stdout.getvalue()

        log_doc_list = \
            so.split(LoggerStreamHandlerBase.YAML_DOCUMENT_SEPARATOR)

        self.assertEqual(len(log_doc_list), 3)

        yaml_dict = yaml.safe_load(log_doc_list[1])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.INFO.name,
            LogElementEnum.PATH.value: class_path,
            LogElementEnum.METHOD.value: method_name,
            LogElementEnum.LINE_NUMBER.value: 366,
            LogElementEnum.MESSAGE.value: msg_1,
            'children': [
                {
                    LogElementEnum.LOG_LEVEL.value: LogLevelEnum.ERROR.name,
                    LogElementEnum.PATH.value: class_path,
                    LogElementEnum.METHOD.value: method_name,
                    LogElementEnum.LINE_NUMBER.value: 368,
                    LogElementEnum.MESSAGE.value: msg_2,
                    'children': [
                        {
                            LogElementEnum.LOG_LEVEL.value:
                                LogLevelEnum.CRITICAL.name,
                            LogElementEnum.PATH.value: class_path,
                            LogElementEnum.METHOD.value: method_name,
                            LogElementEnum.LINE_NUMBER.value: 370,
                            LogElementEnum.MESSAGE.value: msg_1
                        }
                    ]
                }
            ]
        }

        self.__verify_yaml_dict(yaml_dict, expected_yaml_dict)

        yaml_dict = yaml.safe_load(log_doc_list[2])

        expected_yaml_dict = {
            LogElementEnum.LOG_LEVEL.value: LogLevelEnum.ERROR.name,
            LogElementEnum.PATH.value: class_path,
            LogElementEnum.METHOD.value: method_name,
            LogElementEnum.LINE_NUMBER.value: 372,
            LogElementEnum.MESSAGE.value: msg_1
        }

        self.__verify_yaml_dict(yaml_dict, expected_yaml_dict)

    def __verify_yaml_dict(self, yaml_dict, expected_yaml_dict):
        exclude_path = f"\['{LogElementEnum.DATE.value}'\]$"
        cmp_diff = \
            DeepDiff(
                yaml_dict,
                expected_yaml_dict,
                exclude_regex_paths=[exclude_path])
        self.assertFalse(
            cmp_diff,
            f'yaml dict is\n{yaml_dict}\n'
            f'but should be:\n{expected_yaml_dict}\n'
            f'Diff are:\n{cmp_diff}')
        self.assertTrue(LogElementEnum.DATE.value in yaml_dict.keys())
