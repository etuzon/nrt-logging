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


class LogFormat:
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    DEFAULT_YAML_ELEMENTS = \
        (
            LogElementEnum.DATE,
            LogElementEnum.LOG_LEVEL,
            LogElementEnum.PATH,
            LogElementEnum.METHOD,
            LogElementEnum.LINE_NUMBER,
            LogElementEnum.MESSAGE
        )

    __date_format: str = DEFAULT_DATE_FORMAT
    __yaml_elements: set[LogElementEnum] = \
        DEFAULT_YAML_ELEMENTS

    @property
    def date_format(self) -> str:
        return self.__date_format

    @date_format.setter
    def date_format(self, date_format):
        self.__date_format = date_format

    @property
    def yaml_elements(self) -> set[LogElementEnum]:
        return self.__yaml_elements

    @yaml_elements.setter
    def yaml_elements(self, yaml_elements: set[LogElementEnum]):
        self.__yaml_elements = yaml_elements

    @classmethod
    def set_date_format(cls, date_format: str):
        cls.__date_format = date_format

    @classmethod
    def set_yaml_elements(cls, yaml_elements: set[LogElementEnum]):
        cls.__yaml_elements = yaml_elements
