import unittest

from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ConsoleStreamHandler, LogStyleEnum
from tests.test_nrt_logging.test_base import TestBase, NAME_1


class StreamHandlersSnapshotTests(TestBase):
    v_int = 5
    v_s = 's'
    v_dict = {1: 'a', 2: 'b'}

    def setUp(self):
        self._close_loggers_and_delete_logs()

    def tearDown(self):
        self._close_loggers_and_delete_logs()

    def test_console_stream_handler_snapshot(self):
        logger = self.__create_logger_and_console_sh()
        logger.snapshot()

    @classmethod
    def __create_logger_and_console_sh(cls):
        sh = ConsoleStreamHandler()
        sh.style = LogStyleEnum.LINE
        sh.log_level = LogLevelEnum.TRACE
        logger = logger_manager.get_logger(NAME_1)
        logger.add_stream_handler(sh)
        return logger


if __name__ == '__main__':
    unittest.main()
