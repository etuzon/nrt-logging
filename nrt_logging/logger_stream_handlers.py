import ntpath
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from glob import glob
from inspect import stack, FrameInfo
from os.path import exists, getsize
from threading import Lock
from threading import Thread
from typing import IO, Optional, Union
from zipfile import ZipFile, ZIP_DEFLATED

from nrt_logging.exceptions import NotImplementedCodeException
from nrt_logging.log_format import \
    LogElementEnum, LogDateFormat, LogYamlElements
from nrt_logging.log_level import LogLevelEnum


class StreamHandlerEnum(Enum):
    CONSOLE = 'console'
    FILE = 'file'


class LogStyleEnum(Enum):
    YAML = 1
    LINE = 2

    @classmethod
    def build_by_name(cls, name: str):
        name_u = name.upper()

        for style_enum in LogStyleEnum:
            if name_u == style_enum.name:
                return style_enum

        raise ValueError(f'[{name}] is not valid log style name')

    @classmethod
    def build_by_value(cls, value: int):
        for style_enum in LogStyleEnum:
            if value == style_enum.value:
                return style_enum

        raise ValueError(f'[{value}] is not valid log style value')


class ManualDepthEnum(Enum):
    DECREASE = -1
    NO_CHANGE = 0
    INCREASE = 1


@dataclass
class DepthData:
    name: str
    manual_depth_change: int = 0
    total_manual_depth: int = 0


DEFAULT_LOG_STYLE = LogStyleEnum.LINE
DEFAULT_LOG_LEVEL = LogLevelEnum.INFO


class FileSizeEnum(Enum):
    B = 1
    KB = 10 ** 3
    MB = 10 ** 6
    GB = 10 ** 9
    TB = 10 ** 12

    @property
    def bytes(self) -> int:
        return self._value_

    @classmethod
    def build(cls, name: str):
        name_u = name.upper()

        for file_size_enum in cls:
            if name_u == file_size_enum.name:
                return file_size_enum

        raise ValueError(f'[{name}] is not valid file size name')

    @classmethod
    def get_bytes(cls, file_size_str: str) -> int:
        if ' ' in file_size_str:
            return cls.__get_bytes_for_str_with_space(file_size_str)

        return cls.__get_bytes_for_str_without_space(file_size_str)

    @classmethod
    def __get_bytes_for_str_with_space(cls, file_size_str: str) -> int:
        file_size_split = file_size_str.split(' ')

        if len(file_size_split) != 2:
            raise ValueError(
                f'File size [{file_size_str}] is with invalid syntax')

        num = int(file_size_split[0])

        if num <= 0:
            raise ValueError(
                f'File size [{file_size_str}] has invalid syntax')

        return num * cls.build(file_size_split[1]).bytes

    @classmethod
    def __get_bytes_for_str_without_space(cls, file_size_str: str) -> int:
        if len(file_size_str) > 2:
            try:
                file_size = FileSizeEnum.build(file_size_str[-2:])
                num = cls.__num_str_to_int(
                    file_size_str[:-2], file_size_str)
                return num * file_size.bytes
            except ValueError:
                pass

        if len(file_size_str) >= 2:
            file_size = FileSizeEnum.build(file_size_str[-1:])
            num = cls.__num_str_to_int(
                file_size_str[:-1], file_size_str)
            return num * file_size.bytes

        raise ValueError(
            f'File size [{file_size_str}] has invalid syntax')

    @classmethod
    def __num_str_to_int(cls, num_str: str, s: str):
        if not num_str.isdigit():
            raise ValueError(f'File size [{s}] has invalid syntax')

        num = int(num_str)

        if num <= 0:
            raise ValueError(f'File size [{s}] has invalid syntax')

        return num


DEFAULT_MAX_FILE_SIZE = 10 * FileSizeEnum.MB.bytes
DEFAULT_FILES_AMOUNT = 10


class LoggerStreamHandlerBase(ABC):
    YAML_SPACES_SEPARATOR = ' ' * 2
    YAML_CHILDREN_SPACES_SEPARATOR = ' ' * 4
    YAML_DOCUMENT_SEPARATOR = '---'

    LOG_LINE_DEFAULT_TEMPLATE = \
        f'{LogElementEnum.DATE.line_format}' \
        f' [{LogElementEnum.LOG_LEVEL.line_format}]'\
        f' [{LogElementEnum.PATH.line_format}.' \
        f'{LogElementEnum.METHOD.line_format}'\
        f':{LogElementEnum.LINE_NUMBER.line_format}]' \
        f' {LogElementEnum.MESSAGE.line_format}'

    _log_date_format: Optional[LogDateFormat] = None
    _log_yaml_elements: Optional[LogYamlElements] = None

    _stream: Optional[IO] = None

    _lock: Lock
    __stack_log_start_index: int
    __stack_log_increase_start_index: int
    __stack_log_decrease_start_index: int
    _log_level: Optional[LogLevelEnum] = None
    _style: Optional[LogStyleEnum] = None
    _name: Optional[str] = None
    _depth: int
    _depth_list: list[DepthData]
    _increase_depth_list: list[str]
    _decrease_depth_list: list[str]

    _log_line_template: Optional[str] = None

    _is_debug: bool = False

    def __init__(
            self,
            stack_log_start_index: int,
            stack_log_increase_start_index: int = 3,
            stack_log_decrease_start_index: int = 3):

        self.__stack_log_start_index = stack_log_start_index
        self.__stack_log_increase_start_index = stack_log_increase_start_index
        self.__stack_log_decrease_start_index = stack_log_decrease_start_index

        if self._log_level is None:
            self._log_level = DEFAULT_LOG_LEVEL

        if self._style is None:
            self._style = DEFAULT_LOG_STYLE

        if self._log_line_template is None:
            self._log_line_template = self.LOG_LINE_DEFAULT_TEMPLATE

        if self._log_date_format is None:
            self._log_date_format = LogDateFormat()

        if self._log_yaml_elements is None:
            self._log_yaml_elements = LogYamlElements()

        self._depth = 0
        self._depth_list = []
        self._increase_depth_list = []
        self._decrease_depth_list = []
        self._lock = Lock()

    @abstractmethod
    def critical(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def error(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def warn(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def info(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def debug(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def trace(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        raise NotImplementedCodeException

    @abstractmethod
    def close(self):
        raise NotImplementedCodeException

    def increase_depth(self):
        if self.is_debug:
            msg = \
                'NRT-Logging Increase Depth DEBUG\n'\
                'Stack Log Increase Start Index:'\
                f' {self.__stack_log_increase_start_index}'
            self.debug(msg)

        stack_str_list, _ = \
            self.__get_stack_list(
                start_index=self.__stack_log_increase_start_index)

        self._increase_depth_list.append(stack_str_list[0])

    def decrease_depth(self, level: int = 1):
        if level < 1:
            return

        if self.is_debug:
            msg = \
                'NRT-Logging Decrease Depth DEBUG\n'\
                'Stack Log Decrease Start Index:'\
                f' {self.__stack_log_decrease_start_index}'
            self.debug(msg)

        stack_str_list, _ = \
            self.__get_stack_list(
                start_index=self.__stack_log_decrease_start_index)

        fm_name = stack_str_list[0]
        drop_list = []

        for i, depth in enumerate(reversed(self._depth_list)):
            if depth.name == fm_name and depth.manual_depth_change == 1:
                level -= 1
                drop_list.append(len(self._depth_list) - 1 - i)

                if self._depth > 0:
                    self._depth -= 1

        for drop_index in drop_list:
            self._depth_list.pop(drop_index)

        self._decrease_depth_list.append(fm_name)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def style(self) -> LogStyleEnum:
        return self._style

    @style.setter
    def style(self, style: LogStyleEnum):
        self._style = style

    @property
    def log_level(self) -> LogLevelEnum:
        return self._log_level

    @log_level.setter
    def log_level(self, log_level: LogLevelEnum):
        self._log_level = log_level

    @property
    def log_date_format(self) -> LogDateFormat:
        return self._log_date_format

    @log_date_format.setter
    def log_date_format(self, log_date_format: LogDateFormat):
        self._log_date_format = log_date_format

    @property
    def log_yaml_elements(self) -> LogYamlElements:
        return self._log_yaml_elements

    @log_yaml_elements.setter
    def log_yaml_elements(
            self,
            log_yaml_elements:
            Union[LogYamlElements, list[LogElementEnum], set[LogElementEnum]]):

        self._log_yaml_elements = LogYamlElements.build(log_yaml_elements)

    @property
    def log_line_template(self) -> str:
        return self._log_line_template

    @log_line_template.setter
    def log_line_template(self, log_line_template: str):
        self._log_line_template = log_line_template

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @is_debug.setter
    def is_debug(self, is_debug: bool):
        self._is_debug = is_debug

    def _log(
            self,
            log_level: LogLevelEnum,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if log_level >= self.log_level:
            stack_str_list, stack_list = \
                self.__get_stack_list(start_index=self.__stack_log_start_index)

            if self.is_debug:
                msg += self.__add_debug_to_message()

            manual_depth = \
                self.__update_manual_depth(stack_str_list[0], manual_depth)

            log_str = \
                self.__create_log_str(
                    msg, log_level, stack_str_list, stack_list, manual_depth)

            self.__write(f'{log_str}\n')

    def __get_latest_fm_depth(self, fm_name: str) -> Optional[DepthData]:
        for fm_depth in reversed(self._depth_list):
            if fm_name == fm_depth.name:
                return fm_depth

        return None

    def __create_log_str(
            self,
            msg: str,
            log_level: LogLevelEnum,
            stack_str_list: list[str],
            stack_list: list[FrameInfo],
            manual_depth: ManualDepthEnum):
        if self._depth_list:
            return \
                self.__create_log_str_on_depth_plus(
                    msg, log_level, stack_str_list, stack_list, manual_depth)

        return \
            self.__create_log_str_on_depth_0(
                msg, log_level, stack_str_list, stack_list)

    def __update_manual_depth(
            self, fm_name: str, manual_depth: ManualDepthEnum):

        if manual_depth == ManualDepthEnum.NO_CHANGE \
                and fm_name in self._increase_depth_list:
            self._increase_depth_list.remove(fm_name)
            return ManualDepthEnum.INCREASE

        return manual_depth

    def __create_log_str_on_depth_0(
            self,
            msg: str,
            log_level: LogLevelEnum,
            stack_str_list: list[str],
            stack_list: list[FrameInfo]) -> str:

        fm_name = stack_str_list[0]

        self._depth_list.append(DepthData(name=fm_name))

        if self.style == LogStyleEnum.YAML:
            return \
                self.YAML_DOCUMENT_SEPARATOR \
                + self.__create_yaml_elements_str(
                    msg, log_level, False, stack_list)

        if self.style == LogStyleEnum.LINE:
            return self.__create_line_element_str(
                msg, log_level, False, stack_list)

        raise NotImplementedCodeException()

    def __create_log_str_on_depth_plus(
            self,
            msg: str,
            log_level: LogLevelEnum,
            stack_str_list: list[str],
            stack_list: list[FrameInfo],
            manual_depth: ManualDepthEnum):

        fm_name = stack_str_list[0]
        parent_stack_list = stack_str_list[1:]
        expected_parent_fm_name = self._depth_list[-1].name

        is_child = \
            self.__update_depth(
                fm_name,
                stack_str_list,
                expected_parent_fm_name,
                parent_stack_list,
                manual_depth)

        return \
            self.__create_log_str_prefix(is_child) \
            + self.__create_log_str_suffix(
                msg, log_level, is_child, stack_list)

    def __create_log_str_suffix(
            self, msg: str,
            log_level: LogLevelEnum,
            is_child: bool,
            stack_list: list[FrameInfo]):

        if self.style == LogStyleEnum.YAML:
            return self.__create_yaml_elements_str(
                msg, log_level, is_child, stack_list)

        if self.style == LogStyleEnum.LINE:
            return self.__create_line_element_str(
                msg, log_level, is_child, stack_list)

        raise NotImplementedCodeException()

    def __create_log_str_prefix(self, is_child: bool):
        if is_child:
            return self.__create_prefix_log_str_for_child()

        if self._depth == 0 and self.style == LogStyleEnum.YAML:
            return f'{self.YAML_DOCUMENT_SEPARATOR}'

        return ''

    def __create_prefix_log_str_for_child(self):
        depth_4_spaces = \
            ''.join(
                [
                    self.YAML_CHILDREN_SPACES_SEPARATOR
                    for _ in range(self._depth - 1)
                ])
        if self.style == LogStyleEnum.YAML:
            return f'{depth_4_spaces}children:'

        if self.style == LogStyleEnum.LINE:
            return f'{self.YAML_SPACES_SEPARATOR}{depth_4_spaces}children:'

        raise NotImplementedCodeException()

    def __update_depth(
            self,
            fm_name: str,
            stack_list: list[str],
            expected_parent_fm_name: str,
            parent_stack_list: list[str],
            manual_depth: ManualDepthEnum) -> bool:
        """
        Update log depth.

        @param fm_name: Frame name.
        @param stack_list:  Stack list.
        @param expected_parent_fm_name: Expected parent frame name.
        @param parent_stack_list:  parent frame stack list.
        @param manual_depth: Manual depth.
        @return: True in case increase depth, else False.
        """

        # In case this is log in child method
        if self.__is_increased_child_depth(
                expected_parent_fm_name, parent_stack_list):
            self.__update_depth_for_increased_child_depth(fm_name)
            return True

        # In case the log is in the same method of previous log
        if self.__is_child_in_previous_child_depth(
                expected_parent_fm_name, stack_list):
            is_child = \
                self.__update_depth_for_change_in_manual_depth(
                    fm_name, manual_depth)
            return is_child

        # In case go up in the stack so search previous parent
        self.__update_depth_for_go_up_in_stack(
            stack_list, manual_depth)
        return False

    def __update_depth_for_go_up_in_stack(
            self, stack_list: list[str], manual_depth: ManualDepthEnum):

        reverse_depth = 0

        for i, parent in enumerate(reversed(self._depth_list)):
            if parent.name in stack_list:
                self._depth -= reverse_depth

                if self._depth < 0:
                    self._depth = 0

                for _ in range(i):
                    self._depth_list.pop()

                if manual_depth.value:
                    self.__update_depth_for_change_in_manual_depth(
                        stack_list[0], manual_depth)
                else:
                    self._depth_list.append(DepthData(name=stack_list[0]))
                return

            reverse_depth += parent.manual_depth_change + 1

        if manual_depth.value:
            self.__update_depth_for_change_in_manual_depth(
                stack_list[0], manual_depth)
        else:
            self._depth_list = [DepthData(name=stack_list[0])]
            self._depth = 0

    def __write(self, s: str):
        self._lock.acquire()
        self._stream.write(s)
        self._lock.release()

    def __get_stack_list(
            self, start_index: int) -> (list[str], list[FrameInfo]):

        stack_str_list = []
        stack_list = stack()[start_index:]

        for sf in stack_list:
            path, method, _ = \
                self.__get_log_path_method_and_line_number_from_sf(sf)
            stack_str_list.append(self.__create_fm_name(path, method))

        return stack_str_list, stack_list

    def __create_yaml_elements_str(
            self,
            msg: str,
            log_level: LogLevelEnum,
            is_child: bool,
            stack_list: list[FrameInfo]) -> str:
        depth_spaces = \
            ''.join(
                [f'{self.YAML_SPACES_SEPARATOR}  '
                 for _ in range(self._depth)])

        yaml_str = ''

        if self._depth > 0:
            if is_child:
                yaml_str = f'\n{depth_spaces[:-2]}- '
            else:
                yaml_str = f'{depth_spaces[:-2]}- '

        sf = stack_list[0]

        path, method, line_number = \
            self.__get_log_path_method_and_line_number_from_sf(sf)

        yaml_elements_str = \
            self.__create_yaml_elements(
                depth_spaces, log_level, path, method, line_number, msg)

        if self._depth > 0:
            yaml_elements_str = \
                yaml_elements_str[len(f'\n{depth_spaces[:-2]}- '):]

        return yaml_str + yaml_elements_str

    def __create_yaml_elements(
            self,
            depth_spaces: str,
            log_level: LogLevelEnum,
            path: str,
            method: str,
            line_number: str,
            msg: str) -> str:

        return \
            ''.join([
                self.__create_yaml_element(
                    yaml_element,
                    depth_spaces,
                    log_level,
                    path, method,
                    line_number,
                    msg)
                for yaml_element in self.log_yaml_elements.yaml_elements
            ])

    def __create_yaml_element(
            self,
            yaml_element: LogElementEnum,
            depth_spaces: str,
            log_level: LogLevelEnum,
            path: str,
            method: str,
            line_number: str,
            msg: str):

        if yaml_element == LogElementEnum.DATE:
            return f'\n{self.__create_yaml_date_element(depth_spaces)}'

        if yaml_element == LogElementEnum.LOG_LEVEL:
            log_level_str = \
                self.__create_yaml_log_level_element(depth_spaces, log_level)
            return f'\n{log_level_str}'

        if yaml_element == LogElementEnum.PATH:
            return f'\n{self.__create_yaml_path_element(path, depth_spaces)}'

        if yaml_element == LogElementEnum.METHOD:
            return \
                f'\n{self.__create_yaml_method_element(method, depth_spaces)}'

        if yaml_element == LogElementEnum.LINE_NUMBER:
            return \
                '\n' + self.__create_yaml_line_number_element(
                    line_number, depth_spaces)

        if yaml_element == LogElementEnum.MESSAGE:
            return \
                '\n' \
                f'{self.__create_yaml_line_message_element(msg, depth_spaces)}'

        raise NotImplementedCodeException(
            f'Bug: Yaml element {yaml_element} not implemented')

    def __create_line_element_str(
            self,
            msg: str,
            log_level: LogLevelEnum,
            is_child: bool,
            stack_list: list[FrameInfo]) -> str:
        depth_spaces = \
            ''.join(
                [f'{self.YAML_SPACES_SEPARATOR}  '
                 for _ in range(self._depth)])

        sf = stack_list[0]

        path, method, line_number = \
            self.__get_log_path_method_and_line_number_from_sf(sf)

        return \
            self.__create_line_element(
                depth_spaces,
                log_level,
                path,
                method,
                line_number,
                msg,
                is_child)

    def __create_line_element(
            self,
            depth_spaces: str,
            log_level: LogLevelEnum,
            path: str,
            method: str,
            line_number: str,
            msg: str,
            is_child: bool) -> str:

        log_line = self.log_line_template\
            .replace(
                LogElementEnum.DATE.line_format,
                datetime.now().strftime(self.log_date_format.date_format))\
            .replace(LogElementEnum.LOG_LEVEL.line_format, log_level.name)\
            .replace(LogElementEnum.PATH.line_format, path)\
            .replace(LogElementEnum.METHOD.line_format, method)\
            .replace(LogElementEnum.LINE_NUMBER.line_format, line_number)\
            .replace(LogElementEnum.MESSAGE.line_format, msg)

        if '\n' in log_line:
            multiline_operator = self.__get_yaml_multiline_operator(log_line)
            depth_spaces_of_str = \
                f'\n{depth_spaces}{self.YAML_CHILDREN_SPACES_SEPARATOR}'
            log_line_list = log_line.split('\n')
            log_line_with_tabs = depth_spaces_of_str.join(log_line_list)

            line_log = \
                f'{depth_spaces}' \
                f'- log: {multiline_operator}' \
                f'{depth_spaces_of_str}{log_line_with_tabs}'
        else:
            line_log = f'{depth_spaces}- log: {log_line}'

        if is_child:
            line_log = f'\n{line_log}'

        return line_log

    def __create_yaml_date_element(self, depth_spaces: str) -> str:
        return \
            f'{depth_spaces}{LogElementEnum.DATE.value}:' \
            f' {datetime.now().strftime(self.log_date_format.date_format)}'

    def __update_depth_for_manual_increased_child_depth(self, fm_name: str):
        latest_fm_depth = self.__get_latest_fm_depth(fm_name)
        depth_data = DepthData(name=fm_name)
        depth_data.manual_depth_change = 1
        depth_data.total_manual_depth = latest_fm_depth.total_manual_depth + 1
        self._depth += 1
        self._depth_list.append(depth_data)

    def __update_depth_for_manual_decreased_child_depth(self, fm_name: str):
        latest_fm_depth = self.__get_latest_fm_depth(fm_name)

        if self._depth > 0 \
                and latest_fm_depth.total_manual_depth > 0:
            depth_data = DepthData(name=fm_name)
            depth_data.manual_depth_change = -1
            depth_data.total_manual_depth = \
                latest_fm_depth.total_manual_depth - 1
            self._depth -= 1

    def __update_depth_for_increased_child_depth(self, fm_name: str):
        self._depth_list.append(DepthData(name=fm_name))
        self._depth += 1

    def __update_depth_for_change_in_manual_depth(
            self, fm_name: str, manual_depth: ManualDepthEnum):
        if manual_depth == ManualDepthEnum.INCREASE:
            self.__update_depth_for_manual_increased_child_depth(fm_name)
            return True

        if manual_depth == ManualDepthEnum.DECREASE:
            self.__update_depth_for_manual_decreased_child_depth(fm_name)

        return False

    def __add_debug_to_message(self) -> str:
        debug_st_str_list, _ = self.__get_stack_list(start_index=1)
        return \
            '\nNRT-Logging DEBUG:\n' \
            f'Start Index: {self.__stack_log_start_index}\n' \
            + '\n'.join(debug_st_str_list)

    @classmethod
    def set_log_level(cls, level: LogLevelEnum):
        cls._log_level = level

    @classmethod
    def set_log_style(cls, log_style: LogStyleEnum):
        cls._style = log_style

    @classmethod
    def set_log_date_format(cls, log_date_format: LogDateFormat):
        cls._log_date_format = log_date_format

    @classmethod
    def set_log_yaml_elements(cls, log_yaml_elements: LogYamlElements):
        cls._log_yaml_elements = log_yaml_elements

    @classmethod
    def set_log_line_template(cls, log_line_template: str):
        cls._log_line_template = log_line_template

    @classmethod
    def __is_increased_child_depth(
            cls,
            parent_fm_name: str,
            parent_stack_list: list[str]) -> bool:
        return parent_fm_name in parent_stack_list

    @classmethod
    def __is_child_in_previous_child_depth(
            cls, expected_parent_fm_name: str, stack_list: list[str]) -> bool:
        """
        Check if the log is in the same method of previous log.

        @param expected_parent_fm_name:
        @param stack_list:
        @return:
        """

        return expected_parent_fm_name == stack_list[0]

    @classmethod
    def __create_yaml_log_level_element(
            cls, depth_spaces: str, log_level: LogLevelEnum) -> str:
        return \
            f'{depth_spaces}{LogElementEnum.LOG_LEVEL}:' \
            f' {log_level}'

    @classmethod
    def __create_yaml_path_element(cls, path: str, depth_spaces: str) -> str:
        return f'{depth_spaces}{LogElementEnum.PATH.value}: {path}'

    @classmethod
    def __create_yaml_method_element(
            cls, method: str, depth_spaces: str) -> str:
        return f'{depth_spaces}{LogElementEnum.METHOD.value}: {method}'

    @classmethod
    def __create_yaml_line_number_element(
            cls, line_number: str, depth_spaces: str) -> str:
        return \
            f'{depth_spaces}'\
            f'{LogElementEnum.LINE_NUMBER.value}: {line_number}'

    @classmethod
    def __create_yaml_line_message_element(
            cls, msg: str, depth_spaces: str) -> str:

        element = f'{depth_spaces}{LogElementEnum.MESSAGE.value}: '

        if '\n' in msg:
            multiline_operator = cls.__get_yaml_multiline_operator(msg)

            depth_spaces_of_str = \
                f'\n{depth_spaces}{cls.YAML_SPACES_SEPARATOR}'
            message_list = msg.split('\n')
            message_with_tabs = depth_spaces_of_str.join(message_list)
            element += \
                f'{multiline_operator}' \
                f'{depth_spaces_of_str}{message_with_tabs}'
        else:
            element += msg

        return element

    @classmethod
    def __get_log_path_method_and_line_number_from_sf(cls, frame) -> tuple:
        method = frame[3]

        slf = frame[0].f_locals.get('self')

        if slf:
            class_name = slf.__class__.__name__
            path = f'{ntpath.basename(frame[1])}.{class_name}'
        else:
            path = ntpath.basename(frame[1])

        line_number = str(frame[2])

        return path, method, line_number

    @classmethod
    def __create_fm_name(cls, path: str, method: str) -> str:
        return f'{path}_{method}'

    @classmethod
    def __get_yaml_multiline_operator(cls, yaml_text: str):
        return '|' if yaml_text[-1] == '\n' else '|-'


class ConsoleStreamHandler(LoggerStreamHandlerBase):

    def __init__(self):
        super().__init__(
            stack_log_start_index=4,
            stack_log_increase_start_index=3,
            stack_log_decrease_start_index=3)
        self._stream = sys.stdout

    def critical(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.CRITICAL, msg, manual_depth)

    def error(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.ERROR, msg, manual_depth)

    def warn(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.WARN, msg, manual_depth)

    def info(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.INFO, msg, manual_depth)

    def debug(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.DEBUG, msg, manual_depth)

    def trace(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.TRACE, msg, manual_depth)

    def close(self):
        """
        close function not relevant for ConsoleStreamHandler.
        """


class FileStreamHandler(LoggerStreamHandlerBase):
    __ARCHIVE_DATE_FORMAT = '%Y_%m_%d_%H_%M_%S_%f'
    __ZIP_COMPRESSION_LEVEL = 7

    __file_path: str
    __file_path_prefix: str
    __file_extension: str

    __is_limit_file_size: bool = False
    __max_file_size: int = DEFAULT_MAX_FILE_SIZE
    __files_amount: int = DEFAULT_FILES_AMOUNT
    __is_zip: bool = False

    def __init__(self, file_path: str):
        super().__init__(
            stack_log_start_index=5,
            stack_log_increase_start_index=3,
            stack_log_decrease_start_index=3)
        self.__file_path = file_path
        self.__file_path_prefix = self.__get_log_file_path_prefix()
        self.__file_extension = self.__get_log_file_extension()

    def critical(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.CRITICAL, msg, manual_depth)

    def error(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.ERROR, msg, manual_depth)

    def warn(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.WARN, msg, manual_depth)

    def info(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.INFO, msg, manual_depth)

    def debug(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.DEBUG, msg, manual_depth)

    def trace(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self._log(LogLevelEnum.TRACE, msg, manual_depth)

    def close(self):
        if self._stream is not None:
            self._stream.close()

    @property
    def is_limit_file_size(self) -> bool:
        return self.__is_limit_file_size

    @is_limit_file_size.setter
    def is_limit_file_size(self, is_limit_file_size: bool):
        self.__is_limit_file_size = is_limit_file_size

    @property
    def max_file_size(self) -> int:
        return self.__max_file_size

    @max_file_size.setter
    def max_file_size(self, max_file_size: int):
        if max_file_size <= 0:
            raise ValueError('Log file size must be bigger from 0')

        self.__max_file_size = max_file_size

    @property
    def files_amount(self) -> int:
        return self.__files_amount

    @files_amount.setter
    def files_amount(self, files_amount: int):
        if files_amount < 0:
            raise ValueError('Log files amount cannot be negative number')

        self.__files_amount = files_amount

    @property
    def is_zip(self) -> bool:
        return self.__is_zip

    @is_zip.setter
    def is_zip(self, is_zip: bool):
        self.__is_zip = is_zip

    def _log(
            self,
            log_level: LogLevelEnum,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        self.__limit_file_size()

        self._stream = open(self.__file_path, 'a')
        super()._log(log_level, msg, manual_depth)
        self.close()

    def __limit_file_size(self):
        if self.is_limit_file_size:
            if not exists(self.__file_path):
                return

            file_size = getsize(self.__file_path)

            if file_size >= self.max_file_size:
                self._lock.acquire()
                archive_file_path = self.__archive_log()
                self._lock.release()

                t = \
                    Thread(
                        target=self.__zip_archive_and_limit_file_amount,
                        args=(archive_file_path,))
                t.start()

    def __zip_archive_and_limit_file_amount(self, archive_file_path: str):
        if self.is_zip:
            with ZipFile(
                    f'{archive_file_path}.zip',
                    mode='w',
                    compression=ZIP_DEFLATED,
                    compresslevel=self.__ZIP_COMPRESSION_LEVEL) as z:
                z.write(
                    archive_file_path,
                    arcname=ntpath.basename(archive_file_path))
            os.remove(archive_file_path)

        self.__limit_files_amount()

    def __limit_files_amount(self):
        # if files_amount == 0 than truncate log in __archive_log()
        if self.files_amount > 0:
            files_list = self.__get_archive_files_list()

            if len(files_list) > self.files_amount:
                files_list.sort()
                os.remove(files_list[0])

    def __get_archive_files_list(self):
        return [file for file in glob(f'{self.__file_path_prefix}*')
                if self.__is_archive_file(file)]

    def __archive_log(self) -> Optional[str]:
        if self.files_amount == 0:
            os.remove(self.__file_path)
            return None

        archive_file_path = self.__create_archive_file_path_name()
        os.rename(self.__file_path, archive_file_path)
        return archive_file_path

    def __create_archive_file_path_name(self) -> str:
        archive_suffix = self.__create_archive_suffix(self.__file_extension)
        return f'{self.__file_path_prefix}{archive_suffix}'

    def __get_log_file_path_prefix(self) -> str:
        try:
            dot_index = self.__file_path.rindex('.')
            return self.__file_path[:dot_index]
        except ValueError:
            return self.__file_path

    def __get_log_file_extension(self) -> Optional[str]:
        try:
            dot_index = self.__file_path.rindex(".")
            return self.__file_path[dot_index + 1:]
        except ValueError:
            return None

    def __is_archive_file(self, file_path: str):
        suffix = file_path[len(self.__file_path_prefix) + 1:]

        try:
            suffix = suffix[:suffix.index('.')]
        except ValueError:
            pass

        try:
            datetime.strptime(suffix, self.__ARCHIVE_DATE_FORMAT)
            return True
        except ValueError:
            return False

    @classmethod
    def __create_archive_suffix(cls, file_extension: Optional[str]) -> str:
        if file_extension is not None:
            return f'_{datetime.now().strftime(cls.__ARCHIVE_DATE_FORMAT)}' \
                   f'.{file_extension}'

        return f'_{datetime.now().strftime(cls.__ARCHIVE_DATE_FORMAT)}'
