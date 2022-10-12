import sys
import unittest
from datetime import datetime
from io import StringIO
from typing import Optional

from nrt_logging.log_level import LogLevelEnum

NAME_1 = 'name_1'
NAME_2 = 'name_2'

r_stdout: Optional[StringIO] = None


def stdout_redirect(func):
    def inner(*args, **kwargs):
        temp_stdout = sys.stdout
        sys.stdout = func.__globals__['r_stdout'] = StringIO()

        func(*args, **kwargs)

        sys.stdout = temp_stdout
        func.__globals__['r_stdout'] = None

    return inner


def is_date_in_format(date_str: str, date_format: str):
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


class TestBase(unittest.TestCase):

    def _verify_log_line(
            self,
            log_line: str,
            expected_date_format: str,
            expected_log_level: LogLevelEnum,
            expected_class_path: str,
            expected_method_name: str,
            expected_line_number: int,
            expected_msg: str):

        log_line_split = log_line.split(' ')

        date_1 = log_line_split[0]
        date_2 = log_line_split[1]
        expected_date_list = expected_date_format.split(' ')
        expected_date_format_1 = expected_date_list[0]
        expected_date_format_2 = expected_date_list[1]
        self.assertTrue(is_date_in_format(date_1, expected_date_format_1))
        self.assertTrue(is_date_in_format(date_2, expected_date_format_2))

        self.assertEqual(log_line_split[2], f'[{expected_log_level.name}]')

        expected_code_location = \
            f'{expected_class_path}.{expected_method_name}' \
            f':{expected_line_number}'

        self.assertEqual(log_line_split[3], f'[{expected_code_location}]')

        self.assertEqual(log_line_split[4], expected_msg)
