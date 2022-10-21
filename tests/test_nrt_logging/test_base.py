import os
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
    TEMP_PATH = os.path.join(os.getcwd(), 'temp')

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

        index = 0

        expected_date_format_list = expected_date_format.split(' ')

        for expected_date_format in expected_date_format_list:
            date = log_line_split[index]
            self.assertTrue(is_date_in_format(date, expected_date_format))
            index += 1

        self.assertEqual(f'[{expected_log_level.name}]', log_line_split[index])

        expected_code_location = \
            f'{expected_class_path}.{expected_method_name}' \
            f':{expected_line_number}'

        self.assertEqual(f'[{expected_code_location}]', log_line_split[index + 1])
        self.assertEqual(expected_msg, log_line_split[index + 2])
