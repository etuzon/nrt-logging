import sys
from datetime import datetime
from io import StringIO
from typing import Optional


def is_date_in_format(date_str: str, date_format: str):
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


r_stdout: Optional[StringIO] = None


def stdout_redirect(func):
    def inner(*args, **kwargs):
        temp_stdout = sys.stdout
        sys.stdout = func.__globals__['r_stdout'] = StringIO()

        func(*args, **kwargs)

        sys.stdout = temp_stdout
        func.__globals__['r_stdout'] = None

    return inner


NAME_1 = 'name_1'
NAME_2 = 'name_2'
