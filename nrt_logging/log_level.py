from enum import Enum


class LogLevelEnum(Enum):
    TRACE = 'TRACE', 10
    DEBUG = 'DEBUG', 20
    INFO = 'INFO', 30
    WARN = 'WARN', 40
    ERROR = 'ERROR', 50
    CRITICAL = 'CRITICAL', 60

    def __init__(self, name: str, value: int):
        self.__name = name
        self._value_ = value

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    @classmethod
    def build(cls, name: str):
        name = name.upper()

        for log_enum in LogLevelEnum:
            if name == log_enum.name:
                return log_enum

        raise ValueError(f'[{name}] is not valid log level name')


log_level: LogLevelEnum = LogLevelEnum.INFO
