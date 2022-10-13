from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import logger_manager
from nrt_logging.logger_stream_handlers import ConsoleStreamHandler, LogStyleEnum


sh = ConsoleStreamHandler()
sh.log_level = LogLevelEnum.TRACE
sh.log_style = LogStyleEnum.LINE
logger = logger_manager.get_logger('NAME_1')
logger.add_stream_handler(sh)

logger.info('main level log')
logger.increase_depth()
logger.info('child 1')
logger.increase_depth()
logger.info('child 1_1')
logger.decrease_depth()
logger.info('child 2')
logger.decrease_depth()
logger.info('continue main level')
