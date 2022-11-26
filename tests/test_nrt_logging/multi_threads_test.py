import unittest
from threading import Thread

from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum, ManualDepthEnum
from tests.test_nrt_logging.test_base import \
    TestBase, NAME_1, stdout_redirect, r_stdout

A_MSG_1 = 'A METHOD 1'
A_MSG_2 = 'A METHOD 2'
A_MSG_3 = 'A METHOD 3'
B_MSG_1 = 'B METHOD 1'
C_MSG_1 = 'C METHOD 1'


class LoggerThread1(Thread):
    __LOOP = 50

    __logger: NrtLogger

    def __init__(self):
        super().__init__()
        self.__logger = logger_manager.get_logger(NAME_1)

    def run(self):
        for _ in range(self.__LOOP):
            self.__a1()
            self.__a2()
            self.__a3()

    def __a1(self):
        self.__logger.info(A_MSG_1)
        self.__b()
        self.__logger.info(A_MSG_2)
        self.__logger.info(A_MSG_3)

    def __a2(self):
        self.__logger.info(A_MSG_1)
        self.__b()
        self.__logger.increase_depth()
        self.__logger.info(A_MSG_2)
        self.__logger.snapshot()
        self.__logger.increase_depth()
        self.__logger.info(A_MSG_3)

    def __a3(self):
        self.__logger.info(A_MSG_1)
        self.__logger.snapshot(manual_depth=ManualDepthEnum.INCREASE)
        self.__b()
        self.__logger.increase_depth()
        self.__logger.info(A_MSG_2)
        self.__logger.decrease_depth()
        self.__logger.info(A_MSG_3)

    def __b(self):
        self.__logger.info(B_MSG_1)
        self.__c()

    def __c(self):
        self.__logger.info(C_MSG_1)


class LoggerThread2(Thread):
    __LOOP = 50

    __logger: NrtLogger

    def __init__(self):
        super().__init__()
        self.__logger = logger_manager.get_logger(NAME_1)

    def run(self):
        for _ in range(self.__LOOP):
            self.__logger.info(A_MSG_1)
            self.__logger.increase_depth()
            self.__logger.info(A_MSG_2)
            self.__logger.decrease_depth()


class MultiThreadsTests(TestBase):
    def setUp(self):
        logger_manager.close_all_loggers()

    def tearDown(self):
        logger_manager.close_all_loggers()

    @stdout_redirect
    def test_01_multi_threads_not_crash(self):
        self.__create_logger_and_sh()
        self.__execute_multi_thread_test(LoggerThread1, 200)

    @stdout_redirect
    def test_02_multi_threads_not_crash(self):
        self.__create_logger_and_sh()
        self.__execute_multi_thread_test(LoggerThread2, 200)

    def __execute_multi_thread_test(
            self, logger_thread_cls, loop_amount: int):
        multi_thread_list = []

        for _ in range(loop_amount):
            multi_thread_list.append(logger_thread_cls())

        for multi_thread in multi_thread_list:
            multi_thread.start()

        for multi_thread in multi_thread_list:
            multi_thread.join()

        so = r_stdout.getvalue()
        self.assertFalse('Exception' in so)

    @classmethod
    def __create_logger_and_sh(cls):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        return logger


if __name__ == '__main__':
    unittest.main()
