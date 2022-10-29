from examples.demo_classes.demo_classes import NAME_1, Parent
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


def logging_line_style():
    sh = ConsoleStreamHandler()
    sh.style = LogStyleEnum.LINE
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    p = Parent()
    p.a1()


def logging_yaml_style():
    sh = ConsoleStreamHandler()
    sh.style = LogStyleEnum.YAML
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    p = Parent()
    p.a1()


logging_yaml_style()
