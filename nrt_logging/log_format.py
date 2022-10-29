from dataclasses import dataclass
from enum import Enum


class LogElementEnum(Enum):
    DATE = 'date', '$date$'
    LOG_LEVEL = 'log_level', '$log_level$'
    PATH = 'path', '$path$'
    METHOD = 'method', '$method$'
    LINE_NUMBER = 'line_number', '$line_number$'
    MESSAGE = 'message', '$message$'

    def __init__(self, name: str, line_format: str):
        self.__name = name
        self.__line_format = line_format
        self._value_ = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def line_format(self) -> str:
        return self.__line_format

    def __str__(self):
        return self.value

    @classmethod
    def build(cls, name: str):
        name = name.lower()

        for log_element_enum in LogElementEnum:
            if name == log_element_enum.name:
                return log_element_enum

        raise ValueError(f'[{name}] is not valid log element name')


@dataclass
class LogDateFormat:
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    date_format: str = DEFAULT_DATE_FORMAT


@dataclass
class LogYamlElements:
    DEFAULT_YAML_ELEMENTS = \
        (
            LogElementEnum.DATE,
            LogElementEnum.LOG_LEVEL,
            LogElementEnum.PATH,
            LogElementEnum.METHOD,
            LogElementEnum.LINE_NUMBER,
            LogElementEnum.MESSAGE
        )

    yaml_elements: set[LogElementEnum] = DEFAULT_YAML_ELEMENTS

    @classmethod
    def build(cls, log_yaml_elements):
        if isinstance(log_yaml_elements, list):
            return LogYamlElements(yaml_elements=set(log_yaml_elements))

        return LogYamlElements(yaml_elements=log_yaml_elements)
