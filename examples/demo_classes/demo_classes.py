from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum

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


class Parent:
    MSG_1 = 'MSG_1'
    MSG_2 = 'MSG_2'
    MSG_3 = 'MSG_3'
    INCREASE_MSG = 'INCREASE_MSG'
    DECREASE_MSG = 'DECREASE_MSG'

    __logger: NrtLogger
    __child: Child

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__child = Child()

    def a1(self):
        self.__logger.warn(self.MSG_1)
        self.__child.child_1()

    def a2_manual(self):
        self.__logger.info(self.MSG_2)
        self.__logger.increase_depth()
        self.__logger.info(self.INCREASE_MSG)
        self.__logger.decrease_depth()
        self.__logger.info(self.DECREASE_MSG)
        self.__logger.error(self.MSG_1)
        self.a1()

    def a3_manual(self):
        self.__logger.info(self.MSG_2)
        self.__logger.increase_depth()
        self.__logger.info(self.INCREASE_MSG)
        self.__logger.decrease_depth()
        self.__logger.info(self.DECREASE_MSG)
        self.__logger.error(self.MSG_3)

    def a4_manual(self):
        self.__logger.info(self.MSG_1)
        self.__logger.info(self.INCREASE_MSG, ManualDepthEnum.INCREASE)
        self.__logger.info(self.DECREASE_MSG, ManualDepthEnum.DECREASE)
        self.__logger.error(self.MSG_2)
