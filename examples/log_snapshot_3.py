from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


LOGGER_NAME = 'test1'


class Test:
    __logger: NrtLogger

    i = 1
    j = 2

    def __init__(self):
        self.__logger = logger_manager.get_logger(LOGGER_NAME)

    def a(self):
        z = 3
        self.b()

    def b(self):
        y = 'abcd'
        self.__logger.snapshot(methods_depth=2)


sh = ConsoleStreamHandler()
# Snapshot will be printed in TRACE level
sh.log_level = LogLevelEnum.TRACE
sh.style = LogStyleEnum.LINE
logger = logger_manager.get_logger(LOGGER_NAME)
logger.add_stream_handler(sh)
t = Test()
t.a()
