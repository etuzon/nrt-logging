import os
import unittest

import yaml

from nrt_logging.log_format import LogElementEnum
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum, ManualDepthEnum, FileStreamHandler
from tests.test_nrt_logging.test_base import \
    TestBase, NAME_1, stdout_redirect, r_stdout


FILE_NAME_1 = 'log_test_1.txt'

FILE_PATH_1 = os.path.join(TestBase.TEMP_PATH, FILE_NAME_1)

TEST_FILE_NAME = 'logger_stream_handlers_snapshot_test.py'

MSG_1 = 'aaaaaaaaa'
MSG_2 = 'bbbbbbbbb'


class A:
    __i: int
    __logger: NrtLogger

    def __init__(self, i: int):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__i = i

    def a(self):
        m_i = 4
        self.__logger.info(MSG_1)
        self.__logger.snapshot(manual_depth=ManualDepthEnum.INCREASE)
        self.b(m_i)

    def b(self, i: int):
        self.__i = i
        self.__logger.info(f'{MSG_2}{self.__i}')
        self.__logger.snapshot(
            methods_depth=3, manual_depth=ManualDepthEnum.INCREASE)


class StreamHandlersSnapshotTests(TestBase):
    EXPECTED_METHOD_VARS_STR = 'Method vars:'
    EXPECTED_SELF_STR = 'self:'
    EXPECTED_A_LOGGER_STR = '_A__logger:'

    v_int = 5
    v_s = 's'
    v_dict = {1: 'a', 2: 'b'}

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.TEMP_PATH):
            os.makedirs(cls.TEMP_PATH)

    def tearDown(self):
        self._close_loggers_and_delete_logs()

    @stdout_redirect
    def test_console_line_stream_handler_snapshot(self):
        method_name = 'test_console_line_stream_handler_snapshot'

        m_i = 9
        m_s = 'abc'
        logger = self.__create_logger_and_console_line_sh()
        logger.snapshot()

        so = r_stdout.getvalue()
        log_list = yaml.safe_load(so)

        self.assertEqual(1, len(log_list))

        log = log_list[0]['log']

        log_lines = log.split('\n')

        self.assertIn(
            f'Frame: {TEST_FILE_NAME}'
            f'.{self.__class__.__name__}'
            f'.{method_name}',
            log_lines[1])
        self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[2])
        self.assertIn(f'method_name: {method_name}', log_lines[3])
        self.assertIn(f'm_i: {m_i}', log_lines[4])
        self.assertIn(f'm_s: {m_s}', log_lines[5])
        self.assertIn('logger: ', log_lines[6])
        self.assertIn(self.EXPECTED_SELF_STR, log_lines[7])
        self.assertIn(f'v_dict: {self.v_dict}', log_lines[-4])
        self.assertIn(f'v_int: {self.v_int}', log_lines[-3])
        self.assertIn(f'v_s: {self.v_s}', log_lines[-2])

    def test_file_yaml_stream_handler_snapshot(self):
        self.__create_logger_and_file_yaml_sh()
        z = 10
        c = A(z)
        c.a()

        expected_yml_size = 7

        with open(FILE_PATH_1) as f:
            log_yaml = yaml.safe_load(f.read())

            self.assertEqual(expected_yml_size, len(log_yaml))
            self.assertEqual(MSG_1, log_yaml[LogElementEnum.MESSAGE.element_name])

            children = log_yaml.get('children')
            self.assertEqual(1, len(children))
            child = children[0]

            self.assertEqual(
                'a', child.get(LogElementEnum.METHOD.element_name))
            msg = child.get(LogElementEnum.MESSAGE.element_name)
            self.assertTrue(msg)
            log_lines = msg.split('\n')
            self.assertIn(
                f'Frame: {TEST_FILE_NAME}.{A.__name__}.a', log_lines[1])
            self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[2])
            self.assertIn('m_i: 4', log_lines[3])
            self.assertIn(self.EXPECTED_SELF_STR, log_lines[4])
            self.assertIn(f'_A__i: {z}', log_lines[5])
            self.assertIn(self.EXPECTED_A_LOGGER_STR, log_lines[6])

            children = child.get('children')
            self.assertEqual(1, len(children))
            child = children[0]

            self.assertEqual(
                f'{TEST_FILE_NAME}.{A.__name__}',
                child[LogElementEnum.PATH.element_name])
            self.assertEqual(
                'b',
                child[LogElementEnum.METHOD.element_name])
            self.assertEqual(
                f'{MSG_2}4', child[LogElementEnum.MESSAGE.element_name])

            children = child.get('children')
            self.assertEqual(1, len(children))
            child = children[0]

            self.assertEqual(
                f'{TEST_FILE_NAME}.{A.__name__}',
                child[LogElementEnum.PATH.element_name])
            self.assertEqual(
                'b',
                child[LogElementEnum.METHOD.element_name])

            log_lines = child[LogElementEnum.MESSAGE.element_name].split('\n')

            self.assertIn(
                f'Frame: {TEST_FILE_NAME}.{A.__name__}.b', log_lines[1])
            self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[2])
            self.assertIn('i: 4', log_lines[3])
            self.assertIn(self.EXPECTED_SELF_STR, log_lines[4])
            self.assertIn(f'_A__i: 4', log_lines[5])
            self.assertIn(self.EXPECTED_A_LOGGER_STR, log_lines[6])
            self.assertIn('==============', log_lines[7])
            self.assertIn(
                f'Frame: {TEST_FILE_NAME}.{A.__name__}.a', log_lines[8])
            self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[9])
            self.assertIn('m_i: 4', log_lines[10])
            self.assertIn(self.EXPECTED_SELF_STR, log_lines[11])
            self.assertIn(f'_A__i: 4', log_lines[12])
            self.assertIn(self.EXPECTED_A_LOGGER_STR, log_lines[13])
            self.assertIn('==============', log_lines[14])

            method_name = 'test_file_yaml_stream_handler_snapshot'

            self.assertIn(
                f'Frame: {TEST_FILE_NAME}'
                f'.{self.__class__.__name__}'
                f'.{method_name}',
                log_lines[15])
            self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[16])
            self.assertIn(f'z: {z}', log_lines[17])
            self.assertIn(f'c:', log_lines[18])
            self.assertIn(f'v_dict: {self.v_dict}', log_lines[-4])
            self.assertIn(f'v_int: {self.v_int}', log_lines[-3])
            self.assertIn(f'v_s: {self.v_s}', log_lines[-2])

    @stdout_redirect
    def test_console_yaml_stream_handler_snapshot(self):
        method_name = 'test_console_yaml_stream_handler_snapshot'
        m_i = 19
        m_s = 'abcd'
        logger = self.__create_logger_and_console_yaml_sh()
        logger.snapshot()

        so = r_stdout.getvalue()
        yaml_log = yaml.safe_load(so)
        self.assertEqual(6, len(yaml_log))

        self.assertEqual(
            f'{TEST_FILE_NAME}.{self.__class__.__name__}',
            yaml_log.get(LogElementEnum.PATH.element_name))
        self.assertEqual(
            method_name, yaml_log.get(LogElementEnum.METHOD.element_name))
        log_lines = yaml_log[LogElementEnum.MESSAGE.element_name].split('\n')
        self.assertIn(
            f'Frame: {TEST_FILE_NAME}'
            f'.{self.__class__.__name__}'
            f'.{method_name}',
            log_lines[1])
        self.assertIn(self.EXPECTED_METHOD_VARS_STR, log_lines[2])
        self.assertIn(f'method_name: {method_name}', log_lines[3])
        self.assertIn(f'm_i: {m_i}', log_lines[4])
        self.assertIn(f'm_s: {m_s}', log_lines[5])
        self.assertIn('logger: ', log_lines[6])
        self.assertIn(self.EXPECTED_SELF_STR, log_lines[7])
        self.assertIn(f'v_dict: {self.v_dict}', log_lines[-4])
        self.assertIn(f'v_int: {self.v_int}', log_lines[-3])
        self.assertIn(f'v_s: {self.v_s}', log_lines[-2])

    def test_snapshot_with_invalid_methods_depth_negative(self):
        logger = self.__create_logger_and_console_yaml_sh()

        with self.assertRaises(ValueError):
            logger.snapshot(methods_depth=0)

        with self.assertRaises(ValueError):
            logger.snapshot(methods_depth=-1)

    @classmethod
    def __create_logger_and_console_line_sh(cls):
        return cls.__create_logger_and_console_sh(LogStyleEnum.LINE)

    @classmethod
    def __create_logger_and_console_yaml_sh(cls):
        return cls.__create_logger_and_console_sh(LogStyleEnum.YAML)

    @classmethod
    def __create_logger_and_console_sh(cls, log_style: LogStyleEnum):
        sh = ConsoleStreamHandler()
        sh.style = log_style
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        return logger

    @classmethod
    def __create_logger_and_file_yaml_sh(cls):
        sh = FileStreamHandler(FILE_PATH_1)
        sh.style = LogStyleEnum.YAML
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        return logger


if __name__ == '__main__':
    unittest.main()
