from examples.demo_classes.demo_classes import A, NAME_1
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


sh = ConsoleStreamHandler()
sh.log_level = LogLevelEnum.TRACE
sh.style = LogStyleEnum.LINE
logger = logger_manager.get_logger(NAME_1)
logger.add_stream_handler(sh)

a = A()
a.a3_manual()
