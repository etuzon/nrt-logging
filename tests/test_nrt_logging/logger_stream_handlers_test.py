import os
import unittest

from nrt_logging.logger import logger_manager
from nrt_logging.logger_stream_handlers import \
    LogStyleEnum, FileStreamHandler, ManualDepthEnum
from tests.test_nrt_logging.test_base import NAME_2


class FileStreamHandlerTests(unittest.TestCase):
    FILE_NAME = 'log_test.log'
    PATH = os.path.join(os.getcwd(), 'temp')
    FILE_PATH = os.path.join(PATH, FILE_NAME)

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.PATH):
            os.makedirs(cls.PATH)

    def setUp(self):
        if os.path.exists(self.FILE_PATH):
            os.remove(self.FILE_PATH)

    def tearDown(self):
        os.remove(self.FILE_PATH)

    def test_write_to_log(self):
        sh = FileStreamHandler(self.FILE_PATH)
        sh.log_style = LogStyleEnum.LINE
        logger = logger_manager.get_logger(NAME_2)
        logger.add_stream_handler(sh)
        msg_1 = 'asdf'
        msg_2 = 'qwer'
        child_1 = '1234'
        child_2 = '56789'

        logger.critical(msg_1, ManualDepthEnum.INCREASE)
        logger.error(child_1, ManualDepthEnum.INCREASE)
        logger.warn(child_2)
        logger.info(child_1, ManualDepthEnum.DECREASE)
        logger.debug(child_2, ManualDepthEnum.DECREASE)
        logger.info(msg_2, ManualDepthEnum.DECREASE)


if __name__ == '__main__':
    unittest.main()
