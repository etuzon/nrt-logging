from enum import Enum


class LogLevelEnum(Enum):
    TRACE = 10
    DEBUG = 20
    INFO = 30
    WARN = 40
    ERROR = 50
    CRITICAL = 60

    def __str__(self) -> str:
        return self.name

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, LogLevelEnum) and self.value == other.value

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
        name_u = name.upper()

        for log_enum in LogLevelEnum:
            if name_u == log_enum.name:
                return log_enum

        raise ValueError(f'[{name}] is not valid log level name')


log_level: LogLevelEnum = LogLevelEnum.INFO
