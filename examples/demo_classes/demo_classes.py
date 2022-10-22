from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager


NAME_1 = 'TEST1'
NAME_2 = 'TEST2'


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

    def a2_manual(self):
        self.__logger.info('Test 123')
        self.__logger.increase_depth()
        self.__logger.info('Increase Test 123')
        self.__logger.decrease_depth()
        self.__logger.info('Decrease Test 123')
        self.__logger.error('Error Test 123')
        self.a1()
