from nrt_logging.logger import logger_manager, NrtLogger
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum

NAME_1 = 'name 1'


class Child:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def child_1(self):
        self.__logger.info('Child 1')
        self.child_2()

    def child_2(self):
        self.__logger.info('Child 2')


class A:
    __logger: NrtLogger
    __child: Child

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__child = Child()

    def a1(self):
        self.__logger.warn('Message 1')
        self.__child.child_1()


def logging_line_style():
    sh = ConsoleStreamHandler()
    sh.log_style = LogStyleEnum.LINE
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()


def logging_yaml_style():
    sh = ConsoleStreamHandler()
    sh.log_style = LogStyleEnum.YAML
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()


logging_yaml_style()
