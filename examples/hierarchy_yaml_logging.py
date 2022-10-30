from examples.demo_classes.demo_classes import NAME_1, Parent
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


def logging_style(log_style: LogStyleEnum):
    sh = ConsoleStreamHandler()
    sh.style = log_style
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    p = Parent()
    p.a1()


def logging_line_style():
    logging_style(LogStyleEnum.LINE)


def logging_yaml_style():
    logging_style(LogStyleEnum.YAML)


logging_yaml_style()
