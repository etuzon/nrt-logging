import os
import unittest

import yaml

from nrt_logging.log_format import LogElementEnum
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum, LoggerStreamHandlerBase
from tests.test_nrt_logging.test_base import TestBase, stdout_redirect, r_stdout, is_date_in_format


class LoggerManagerConfigTests(TestBase):
    TEST_FILE_NAME = 'config_test.py'

    BASELINE_PATH = os.path.join('baseline', 'config_files')

    MULTI_SH_NO_INHERITANCE_FILE_NAME = \
        'logging_config_multi_sh_no_inheritance.yaml'
    MULTI_LOGGER_INHERITANCE_FILE_NAME = \
        'logging_config_multi_logger_inheritance.yaml'
    LOGGER_LINE_FILE_NAME = 'logging_config_line.yaml'
    LOGGER_YAML_FILE_NAME = 'logging_config_yaml.yaml'

    MULTI_SH_NO_INHERITANCE_FILE_PATH = \
        os.path.join(BASELINE_PATH, MULTI_SH_NO_INHERITANCE_FILE_NAME)
    MULTI_LOGGER_INHERITANCE_FILE_PATH = \
        os.path.join(BASELINE_PATH, MULTI_LOGGER_INHERITANCE_FILE_NAME)
    LOGGER_LINE_FILE_PATH = \
        os.path.join(BASELINE_PATH, LOGGER_LINE_FILE_NAME)
    LOGGER_YAML_FILE_PATH = \
        os.path.join(BASELINE_PATH, LOGGER_YAML_FILE_NAME)

    FILE_NAME_1 = 'log_test_1.txt'
    FILE_NAME_2 = 'log_test_2.txt'
    FILE_PATH_1 = os.path.join(TestBase.TEMP_PATH, FILE_NAME_1)
    FILE_PATH_2 = os.path.join(TestBase.TEMP_PATH, FILE_NAME_2)

    LOGGER_NAME_1 = 'TEST1'
    LOGGER_NAME_2 = 'TEST2'

    expected_class_path = None

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.TEMP_PATH):
            os.makedirs(cls.TEMP_PATH)

        cls.expected_class_path = f'{cls.TEST_FILE_NAME}.{cls.__name__}'

    def setUp(self):
        if os.path.exists(self.FILE_PATH_1):
            os.remove(self.FILE_PATH_1)
        if os.path.exists(self.FILE_PATH_2):
            os.remove(self.FILE_PATH_2)

    def tearDown(self):
        if os.path.exists(self.FILE_PATH_1):
            os.remove(self.FILE_PATH_1)
        if os.path.exists(self.FILE_PATH_2):
            os.remove(self.FILE_PATH_2)

        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.close_logger(self.LOGGER_NAME_2)

    @stdout_redirect
    def test_logging_config_multi_sh_no_inheritance(self):
        logger_manager.set_config(
            file_path=self.MULTI_SH_NO_INHERITANCE_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        msg_info_1 = 'Info_123'
        msg_debug_1 = 'Debug_123'

        logger.info(msg_info_1)
        logger.debug(msg_debug_1)

        console_log_list = yaml.safe_load(r_stdout.getvalue())

        self.assertEqual(len(console_log_list), 1)

        log_split = console_log_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(log_split[1], '%Y-%m'))
        self.assertEqual(msg_info_1, log_split[2])

        with open(self.FILE_PATH_1) as f:
            file_log_list = yaml.safe_load(f.read())

        self.assertEqual(2, len(file_log_list))

        log_split = file_log_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_info_1, log_split[2])

        log_split = file_log_list[1]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_debug_1, log_split[2])

    @stdout_redirect
    def test_logging_config_multi_logger_inheritance(self):
        logger_manager.set_config(
            file_path=self.MULTI_LOGGER_INHERITANCE_FILE_PATH)
        logger1 = logger_manager.get_logger(self.LOGGER_NAME_1)
        logger2 = logger_manager.get_logger(self.LOGGER_NAME_2)

        msg_warn_1 = 'Warn_123'
        msg_warn_2 = 'Warn_aaa123'

        msg_error_1 = 'Error_234'
        msg_error_2 = 'Error_aaa234'

        msg_info_1 = 'Info_123'
        msg_info_2 = 'Info_aaa123'

        msg_debug_1 = 'Debug_123'
        msg_debug_2 = 'Debug_aaa123'

        logger1.warn(msg_warn_1)
        logger1.error(msg_error_1)
        logger1.info(msg_info_1)
        logger1.debug(msg_debug_1)

        logger2.warn(msg_warn_2)
        logger2.error(msg_error_2)
        logger2.info(msg_info_2)
        logger2.debug(msg_debug_2)

        console_log_list = yaml.safe_load(r_stdout.getvalue())

        self.assertEqual(2, len(console_log_list))

        log_split = console_log_list[0]['log'].split(' ')
        self.assertEqual('Test123', log_split[0])
        self.assertEqual(msg_warn_1, log_split[1])

        log_split = console_log_list[1]['log'].split(' ')
        self.assertEqual('Test123', log_split[0])
        self.assertEqual(msg_error_1, log_split[1])

        with open(self.FILE_PATH_1) as f:
            file_log_list = yaml.safe_load(f.read())

        self.assertEqual(4, len(file_log_list))

        log_split = file_log_list[0]['log'].split(' ')
        self.assertEqual('Test1', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_warn_1, log_split[2])

        log_split = file_log_list[1]['log'].split(' ')
        self.assertEqual('Test1', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_error_1, log_split[2])

        log_split = file_log_list[2]['log'].split(' ')
        self.assertEqual('Test1', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_info_1, log_split[2])

        log_split = file_log_list[3]['log'].split(' ')
        self.assertEqual('Test1', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y'))
        self.assertEqual(msg_debug_1, log_split[2])

        logger_manager.close_logger(self.LOGGER_NAME_1)

        with open(self.FILE_PATH_2) as f:
            log_2 = yaml.safe_load(f.read())

        self.assertEqual(
            LogLevelEnum.ERROR.name, log_2.get(LogElementEnum.LOG_LEVEL.name))
        self.assertTrue(
            is_date_in_format(str(log_2.get(LogElementEnum.DATE.name)), '%Y'))
        self.assertEqual(msg_error_2, log_2.get(LogElementEnum.MESSAGE.name))

    def test_recreate_logger_line(self):
        msg_1 = 'msg_1'
        msg_2 = 'msg_2'
        child_1 = 'child_1'
        child_2 = 'child_2'

        logger_manager.set_config(
            file_path=self.LOGGER_LINE_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_1)

        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_LINE_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_2)

        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_LINE_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_1)
        logger.info(child_1, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_2, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_1, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_2)
        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_LINE_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_2)
        logger.info(child_2, manual_depth=ManualDepthEnum.INCREASE)

        with open(self.FILE_PATH_1) as f:
            log_list = yaml.safe_load(f.read())

        self.assertEqual(4, len(log_list))

        log_split = log_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(msg_1, log_split[2])

        log_split = log_list[1]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(msg_2, log_split[2])

        log_split = log_list[2]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(msg_1, log_split[2])

        child_list = log_list[2]['children']
        self.assertEqual(1, len(child_list))
        log_split = child_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(child_1, log_split[2])

        child_list = child_list[0]['children']
        self.assertEqual(1, len(child_list))
        log_split = child_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(child_2, log_split[2])

        child_list = child_list[0]['children']
        self.assertEqual(2, len(child_list))
        log_split = child_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(child_1, log_split[2])

        log_split = child_list[1]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(child_2, log_split[2])

        log_split = log_list[3]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(msg_2, log_split[2])

        child_list = log_list[3]['children']
        self.assertEqual(1, len(child_list))
        log_split = child_list[0]['log'].split(' ')
        self.assertEqual('Test', log_split[0])
        self.assertTrue(is_date_in_format(str(log_split[1]), '%Y-%m'))
        self.assertEqual(child_2, log_split[2])

    def test_recreate_logger_yaml(self):
        msg_1 = 'msg_1'
        msg_2 = 'msg_2'
        child_1 = 'child_1'
        child_2 = 'child_2'

        logger_manager.set_config(
            file_path=self.LOGGER_YAML_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.debug(msg_1)

        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_YAML_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_2)

        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_YAML_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_1)
        logger.info(child_1, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_2, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_1, manual_depth=ManualDepthEnum.INCREASE)
        logger.info(child_2)
        logger_manager.close_logger(self.LOGGER_NAME_1)
        logger_manager.set_config(
            file_path=self.LOGGER_YAML_FILE_PATH)
        logger = logger_manager.get_logger(self.LOGGER_NAME_1)

        logger.info(msg_2)
        logger.info(child_2, manual_depth=ManualDepthEnum.INCREASE)

        with open(self.FILE_PATH_1) as f:
            f_str = f.read()
            yaml_list = \
                [
                    yaml.safe_load(y_doc)
                    for y_doc in f_str.split(
                        LoggerStreamHandlerBase.YAML_DOCUMENT_SEPARATOR)
                ]

        yaml_list.pop(0)
        self.assertEqual(4, len(yaml_list))

        self.__verify_log_yaml(
            yaml_list[0],
            '%Y-%m',
            LogLevelEnum.DEBUG,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            284,
            msg_1)
        self.__verify_log_yaml(
            yaml_list[1],
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            291,
            msg_2)

        self.__verify_log_yaml(
            yaml_list[2],
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            298,
            msg_1)

        children = yaml_list[2].get('children')
        self.assertEqual(1, len(children))
        child = children[0]
        self.__verify_log_yaml(
            child,
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            299,
            child_1)

        children = child.get('children')
        self.assertEqual(1, len(children))
        child = children[0]
        self.__verify_log_yaml(
            child,
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            300,
            child_2)

        children = child.get('children')
        self.assertEqual(2, len(children))
        child = children[0]
        self.__verify_log_yaml(
            child,
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            301,
            child_1)
        child = children[1]
        self.__verify_log_yaml(
            child,
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            302,
            child_2)

        self.__verify_log_yaml(
            yaml_list[3],
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            308,
            msg_2)

        children = yaml_list[3].get('children')
        self.assertEqual(1, len(children))
        child = children[0]
        self.__verify_log_yaml(
            child,
            '%Y-%m',
            LogLevelEnum.INFO,
            self.expected_class_path,
            'test_recreate_logger_yaml',
            309,
            child_2)

    def __verify_log_yaml(
            self,
            log_yaml: dict,
            expected_date_format: str,
            expected_log_level: LogLevelEnum,
            expected_path: str,
            expected_method: str,
            expected_line_number: int,
            expected_message: str):

        self.assertTrue(
            is_date_in_format(
                str(log_yaml.get(LogElementEnum.DATE.name)),
                expected_date_format))
        self.assertEqual(
            expected_log_level.name,
            log_yaml.get(LogElementEnum.LOG_LEVEL.name))
        self.assertEqual(
            expected_path,
            log_yaml.get(LogElementEnum.PATH.name))
        self.assertEqual(
            expected_method,
            log_yaml.get(LogElementEnum.METHOD.name))
        self.assertEqual(
            expected_line_number,
            log_yaml.get(LogElementEnum.LINE_NUMBER.name))
        self.assertEqual(
            expected_message,
            log_yaml.get(LogElementEnum.MESSAGE.name))


if __name__ == '__main__':
    unittest.main()
