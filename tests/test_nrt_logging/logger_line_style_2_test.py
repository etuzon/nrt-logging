import unittest

import yaml

from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum
from tests.test_nrt_logging.test_base import \
    TestBase, NAME_1, stdout_redirect, r_stdout

TEST_FILE_NAME = 'logger_line_style_2_test.py'

A_MSG_1 = 'A METHOD 1'
B_MSG_1 = 'B METHOD 1'
C_MSG_1 = 'C METHOD 1'
D_MSG_1 = 'D METHOD 1'
D_MSG_2 = 'D METHOD 2'
E_MSG_1 = 'E METHOD 1'
F_MSG_1 = 'F METHOD 1'
G_MSG_1 = 'G METHOD 1'
H_MSG_1 = 'H METHOD 1'


class ComplexLogs1:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def a(self):
        self.b()
        self.__logger.info(A_MSG_1)

    def b(self):
        self.__logger.info(B_MSG_1)
        self.c()

    def c(self):
        self.d()

    def d(self):
        self.__logger.info(D_MSG_1)
        self.__logger.info(D_MSG_2)

    def e(self):
        self.__logger.info(E_MSG_1)
        self.f()

    def f(self):
        self.g()
        self.__logger.info(F_MSG_1)

    def g(self):
        self.h()
        self.__logger.info(G_MSG_1)

    def h(self):
        self.__logger.info(H_MSG_1)


class ComplexLogs2:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def a(self):
        self.b()
        self.__logger.info(A_MSG_1)

    def b(self):
        self.__logger.info(B_MSG_1)
        self.c()

    def c(self):
        self.d()
        self.__logger.info(C_MSG_1)

    def d(self):
        self.__logger.info(D_MSG_1)
        self.e()
        self.__logger.info(D_MSG_2)

    def e(self):
        self.__logger.info(E_MSG_1)
        self.f()

    def f(self):
        self.__logger.info(F_MSG_1)
        self.g()

    def g(self):
        self.__logger.info(G_MSG_1)
        self.h()

    def h(self):
        self.__logger.info(H_MSG_1)


class RecursiveLogs1:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def a(self, i: int = 3):
        if not i:
            return

        self.__logger.info(f'{A_MSG_1} i={i}')
        self.a(i - 1)


class NrtLoggerManager2Tests(TestBase):

    def setUp(self):
        logger_manager.close_all_loggers()

    def tearDown(self):
        logger_manager.close_all_loggers()

    @stdout_redirect
    def test_complex_logger_structure_1(self):
        self.__create_logger_and_sh()
        cl_1 = ComplexLogs1()
        cl_1.a()
        cl_1.e()
        so = r_stdout.getvalue()

        log_list = yaml.safe_load(so)

        self.assertEqual(5, len(log_list))

        self.assertTrue(B_MSG_1 in log_list[0]['log'])

        children = log_list[0]['children']

        self.assertEqual(2, len(children))
        self.assertTrue(D_MSG_1 in children[0]['log'])
        self.assertTrue(D_MSG_2 in children[1]['log'])

        self.assertTrue(A_MSG_1 in log_list[1]['log'])
        self.assertTrue(E_MSG_1 in log_list[2]['log'])

        children = log_list[2]['children']

        self.assertEqual(1, len(children))

        self.assertTrue(H_MSG_1 in children[0]['log'])

        self.assertTrue(G_MSG_1 in log_list[3]['log'])
        self.assertTrue(F_MSG_1 in log_list[4]['log'])

    @stdout_redirect
    def test_complex_logger_structure_2(self):
        self.__create_logger_and_sh()
        cl_2 = ComplexLogs2()
        cl_2.a()
        cl_2.e()
        so = r_stdout.getvalue()

        log_list = yaml.safe_load(so)

        self.assertEqual(4, len(log_list))

        self.assertTrue(B_MSG_1 in log_list[0]['log'])

        children = log_list[0]['children']

        self.assertEqual(2, len(children))
        self.assertTrue(D_MSG_1 in children[0]['log'])
        self.assertTrue(D_MSG_2 in children[1]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(E_MSG_1 in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(F_MSG_1 in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(G_MSG_1 in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(H_MSG_1 in children[0]['log'])

        self.assertTrue(C_MSG_1 in log_list[1]['log'])
        self.assertTrue(A_MSG_1 in log_list[2]['log'])
        self.assertTrue(E_MSG_1 in log_list[3]['log'])

        children = log_list[3]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(F_MSG_1 in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(G_MSG_1 in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(H_MSG_1 in children[0]['log'])

    @stdout_redirect
    def test_recursive_logger_structure_1(self):
        self.__create_logger_and_sh()
        recursive_logger = RecursiveLogs1()
        recursive_logger.a()

        so = r_stdout.getvalue()

        log_list = yaml.safe_load(so)

        self.assertEqual(1, len(log_list))

        self.assertTrue(f'{A_MSG_1} i=3' in log_list[0]['log'])

        children = log_list[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(f'{A_MSG_1} i=2' in children[0]['log'])

        children = children[0]['children']

        self.assertEqual(1, len(children))
        self.assertTrue(f'{A_MSG_1} i=1' in children[0]['log'])

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
