import os
import unittest
from time import sleep

import yaml
from parameterized import parameterized

from nrt_logging.log_format import \
    LogDateFormat, LogElementEnum, LogYamlElements
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    LogStyleEnum, FileStreamHandler, \
    ManualDepthEnum, FileSizeEnum, ConsoleStreamHandler
from tests.test_nrt_logging.test_base import \
    NAME_2, TestBase


class LogStyleEnumTests(TestBase):

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
    FILE_EXTENSION = 'log'
    FILE_NAME_PREFIX = 'log_test'
    FILE_NAME = f'{FILE_NAME_PREFIX}.{FILE_EXTENSION}'
    FILE_PATH = os.path.join(TestBase.TEMP_PATH, FILE_NAME)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.TEMP_PATH):
            os.makedirs(cls.TEMP_PATH)

    def setUp(self):
        self._close_loggers_and_delete_logs()

    def tearDown(self):
        self._close_loggers_and_delete_logs()

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
            64,
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
            65,
            child_1)

        self._verify_log_line(
            children[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.WARN,
            expected_class_path,
            expected_method_name,
            66,
            child_2)

        self._verify_log_line(
            log_list[1].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            67,
            child_1)

        self._verify_log_line(
            log_list[2].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            69,
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
            71,
            child_1)

        self._verify_log_line(
            log_list[3].get('log'),
            LogDateFormat.DEFAULT_DATE_FORMAT,
            LogLevelEnum.INFO,
            expected_class_path,
            expected_method_name,
            73,
            msg_2)

    def test_write_to_log_and_limit_files_size(self):
        file_size_limitation = 1000
        sh = FileStreamHandler(self.FILE_PATH)
        sh.style = LogStyleEnum.LINE
        sh.log_line_template = LogElementEnum.MESSAGE.line_format
        sh.is_limit_file_size = True
        sh.files_amount = 2
        sh.max_file_size = file_size_limitation
        sh.is_zip = False
        logger = logger_manager.get_logger(NAME_2)
        logger.add_stream_handler(sh)

        for _ in range(11):
            logger.info(self.MSG_100_BYTES)
            sleep(0.05)

        log_files = os.listdir(self.TEMP_PATH)

        self.assertEqual(2, len(log_files))

        log_files.sort()

        archive_1_path = os.path.join(self.TEMP_PATH, log_files[1])

        archive_size = \
            os.path.getsize(archive_1_path)

        self.assertTrue(
            2 * file_size_limitation > archive_size > file_size_limitation)

        with open(archive_1_path) as f:
            log_list = yaml.safe_load(f.read())

        self.assertGreater(len(log_list), 9)

        with open(self.FILE_PATH) as f:
            log_list = yaml.safe_load(f.read())

        self.assertLess(len(log_list), 3)

    def test_set_log_level(self):
        original_log_level = ConsoleStreamHandler().log_level
        updated_log_level = LogLevelEnum.CRITICAL
        ConsoleStreamHandler.set_log_level(updated_log_level)
        self.assertEqual(updated_log_level, ConsoleStreamHandler().log_level)
        self.assertEqual(original_log_level, FileStreamHandler('a').log_level)
        ConsoleStreamHandler.set_log_level(original_log_level)
        self.assertEqual(original_log_level, ConsoleStreamHandler().log_level)

    def test_set_log_date_format(self):
        original_log_date_format = ConsoleStreamHandler().log_date_format
        updated_log_date_format = LogDateFormat(date_format='%Y-%m-%d')
        ConsoleStreamHandler.set_log_date_format(updated_log_date_format)
        self.assertEqual(
            updated_log_date_format.date_format,
            ConsoleStreamHandler().log_date_format.date_format)
        ConsoleStreamHandler.set_log_date_format(original_log_date_format)
        self.assertEqual(
            original_log_date_format.date_format,
            ConsoleStreamHandler().log_date_format.date_format)

    def test_set_log_yaml_elements(self):
        original_log_yaml_elements = ConsoleStreamHandler().log_yaml_elements
        updated_log_yaml_elements = \
            LogYamlElements(yaml_elements={LogElementEnum.DATE})
        ConsoleStreamHandler.set_log_yaml_elements(updated_log_yaml_elements)
        self.assertEqual(
            updated_log_yaml_elements.yaml_elements,
            ConsoleStreamHandler().log_yaml_elements.yaml_elements)
        ConsoleStreamHandler.set_log_yaml_elements(original_log_yaml_elements)
        self.assertEqual(
            original_log_yaml_elements.yaml_elements,
            ConsoleStreamHandler().log_yaml_elements.yaml_elements)

    def test_set_log_line_template(self):
        original_log_line_template = ConsoleStreamHandler().log_line_template
        updated_log_line_template = 'test 123 $message$'
        ConsoleStreamHandler.set_log_line_template(updated_log_line_template)
        self.assertEqual(
            updated_log_line_template,
            ConsoleStreamHandler().log_line_template)
        ConsoleStreamHandler.set_log_line_template(original_log_line_template)
        self.assertEqual(
            original_log_line_template,
            ConsoleStreamHandler().log_line_template)

    def test_invalid_max_file_size_negative(self):
        file_stream_handler = FileStreamHandler('/test.txt')

        with self.assertRaises(ValueError):
            file_stream_handler.max_file_size = 0

        with self.assertRaises(ValueError):
            file_stream_handler.max_file_size = -1

    def test_invalid_files_amount_negative(self):
        file_stream_handler = FileStreamHandler('/test.txt')

        with self.assertRaises(ValueError):
            file_stream_handler.files_amount = -1


class FileSizeEnumTests(TestBase):

    @parameterized.expand([
        [FileSizeEnum.B, 1],
        [FileSizeEnum.KB, 10 ** 3],
        [FileSizeEnum.MB, 10 ** 6],
        [FileSizeEnum.GB, 10 ** 9],
        [FileSizeEnum.TB, 10 ** 12],
    ])
    def test_bytes(self, file_size_enum: FileSizeEnum, expected_size):
        self.assertEqual(expected_size, file_size_enum.bytes)

    @parameterized.expand([
        ['B', FileSizeEnum.B],
        ['kb', FileSizeEnum.KB],
        ['mB', FileSizeEnum.MB],
        ['Gb', FileSizeEnum.GB],
        ['TB', FileSizeEnum.TB],
    ])
    def test_build(
            self, size_str: str, expected_file_size_enum: FileSizeEnum):
        self.assertEqual(
            expected_file_size_enum, FileSizeEnum.build(size_str))

    @parameterized.expand([
        [''], ['k'], ['dd'], ['12'], ['qwer']
    ])
    def test_build_negative(self, value: str):
        with self.assertRaises(ValueError):
            FileSizeEnum.build(value)

    @parameterized.expand([
        ['10 gb', 10 * 1000 * 1000 * 1000],
        ['5gb', 5 * 1000 * 1000 * 1000],
        ['8 B', 8],
        ['234b', 234],
        ['134 Kb', 134 * 1000],
        ['44TB', 44 * 1000 * 1000 * 1000 * 1000],
        ['3 MB', 3 * 1000 * 1000],
        ['50mB', 50 * 1000 * 1000]
    ])
    def test_get_bytes(self, file_size_str: str, expected_bytes: int):
        self.assertEqual(
            expected_bytes, FileSizeEnum.get_bytes(file_size_str))

    @parameterized.expand([
        ['10 gb a'],
        ['-5gb'],
        ['-8 B'],
        ['-234b'],
        ['4 Ks'],
        ['44Tq'],
        ['b'],
        ['0 b'],
        ['0 KB'],
        ['0b'],
        ['0MB'],
        ['3qwe']
    ])
    def test_get_bytes_negative(self, file_size_str: str):
        with self.assertRaises(ValueError):
            FileSizeEnum.get_bytes(file_size_str)


if __name__ == '__main__':
    unittest.main()
