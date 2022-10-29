from examples.demo_classes.demo_classes import \
    NAME_1, Parent, NAME_2
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum

CONFIG_FILE_PATH = 'config/config_2.yaml'

logger_manager.set_config(file_path=CONFIG_FILE_PATH)
logger_1 = logger_manager.get_logger(NAME_1)
a = Parent()
a.a2_manual()
a.a1()
