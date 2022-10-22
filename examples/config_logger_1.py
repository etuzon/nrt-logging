from examples.demo_classes.demo_classes import \
    NAME_1, A, NAME_2
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum

CONFIG_FILE_PATH = 'config/config_1.yaml'

logger_manager.set_config(file_path=CONFIG_FILE_PATH)
logger_1 = logger_manager.get_logger(NAME_1)
a = A()
a.a2_manual()
a.a1()
logger_2 = logger_manager.get_logger(NAME_2)
logger_2.error('Test 1234567')
logger_2.critical('Child 1', ManualDepthEnum.INCREASE)
logger_2.error('Child 2')
logger_2.error('Child 1', ManualDepthEnum.DECREASE)
logger_2.info('Logger will not appear')
logger_2.error('Test Test 2')
