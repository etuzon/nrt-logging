from typing import Optional

from nrt_logging.config import \
    LoggerManagerConfig, LoggerConfig, StreamHandlerConfig, ConfigBase
from nrt_logging.log_format import LogDateFormat
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_stream_handlers import LoggerStreamHandlerBase


class NrtLoggerManager:
    __is_running: bool = False
    __logger_dict: dict[str, NrtLogger]
    __logger_manager_config: Optional[LoggerManagerConfig] = None

    __is_debug: bool = False

    def __init__(self):
        self.__verify_not_initiated()
        self.__logger_dict = {}

    def get_logger(self, name: str) -> NrtLogger:
        yaml_logger = self.__logger_dict.get(name)

        if yaml_logger is None:
            self.__logger_dict[name] = NrtLogger()

        if self.__is_debug:
            self.__logger_dict[name].is_debug = self.__is_debug

        return self.__logger_dict[name]

    def close_logger(self, name):
        logger = self.__logger_dict.get(name)

        if logger:
            logger.close_stream_handlers()
            self.__logger_dict.pop(name)

    def set_config(
            self, file_path: str = None, config: dict = None):

        self.__logger_manager_config = \
            LoggerManagerConfig(file_path, config)

        for lc in self.__logger_manager_config.loggers_config.values():
            self.__build_logger_from_config(lc)

    @property
    def is_debug(self) -> bool:
        return self.__is_debug

    @is_debug.setter
    def is_debug(self, is_debug: bool):
        self.__is_debug = is_debug

    def __build_logger_from_config(self, logger_config: LoggerConfig):
        logger = logger_manager.get_logger(logger_config.name)

        logger_level_set = set()

        for sh_config in logger_config.stream_handler_list:
            sh = \
                self.__build_stream_handler_from_config(
                    sh_config, logger_config)
            logger_level_set.add(sh.log_level)
            logger.add_stream_handler(sh)

        logger.update_log_level(min(logger_level_set), False)

    def __build_stream_handler_from_config(
            self,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig) -> LoggerStreamHandlerBase:

        sh = stream_handler_config.build_stream_handler()

        self.__update_stream_handler_log_level_from_config(
            sh, stream_handler_config, logger_config)
        self.__update_stream_handler_log_style_from_config(
            sh, stream_handler_config, logger_config)
        self.__update_stream_handler_log_date_format_from_config(
            sh, stream_handler_config, logger_config)
        self.__update_stream_handler_log_line_template_from_config(
            sh, stream_handler_config, logger_config)
        self.__update_stream_handler_log_yaml_elements_from_config(
            sh, stream_handler_config, logger_config)
        self.__update_stream_handler_debug_from_config(
            sh, stream_handler_config, logger_config)

        if stream_handler_config.file_path is not None:
            sh.file_path = stream_handler_config.file_path

        return sh

    def __update_stream_handler_log_level_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        log_level_enum = \
            self.__get_inherited_property_from_config(
                ConfigBase.LOG_LEVEL, stream_handler_config, logger_config)

        if log_level_enum is not None:
            sh.log_level = log_level_enum

    def __update_stream_handler_log_style_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        log_style_enum = \
            self.__get_inherited_property_from_config(
                ConfigBase.STYLE, stream_handler_config, logger_config)

        if log_style_enum is not None:
            sh.style = log_style_enum

    def __update_stream_handler_log_date_format_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        date_format = \
            self.__get_inherited_property_from_config(
                ConfigBase.DATE_FORMAT, stream_handler_config, logger_config)

        if date_format is not None:
            sh.log_date_format = LogDateFormat(date_format=date_format)

    def __update_stream_handler_log_line_template_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        log_line_template = \
            self.__get_inherited_property_from_config(
                ConfigBase.LOG_LINE_TEMPLATE,
                stream_handler_config,
                logger_config)

        if log_line_template is not None:
            sh.log_line_template = log_line_template

    def __update_stream_handler_log_yaml_elements_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        log_yaml_elements = \
            self.__get_inherited_property_from_config(
                ConfigBase.LOG_YAML_ELEMENTS,
                stream_handler_config,
                logger_config)

        if log_yaml_elements is not None:
            sh.log_yaml_elements = log_yaml_elements

    def __update_stream_handler_debug_from_config(
            self,
            sh: LoggerStreamHandlerBase,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        is_debug = \
            self.__get_inherited_property_from_config(
                ConfigBase.DEBUG, stream_handler_config, logger_config)

        if is_debug is not None:
            sh.is_debug = is_debug

    def __get_inherited_property_from_config(
            self,
            property_name: str,
            stream_handler_config: StreamHandlerConfig,
            logger_config: LoggerConfig):

        sh_property = getattr(stream_handler_config, property_name, None)
        if sh_property is not None:
            return sh_property

        logger_property = getattr(logger_config, property_name, None)
        if logger_property is not None:
            return logger_property

        logger_manager_property = \
            getattr(self.__logger_manager_config, property_name, None)
        if logger_manager_property is not None:
            return logger_manager_property

        return None

    @classmethod
    def __verify_not_initiated(cls):
        if cls.__is_running:
            raise RuntimeError(
                'NrtLoggerManager should not be initiated.'
                ' Please use yaml_logging')

        cls.__is_running = True


logger_manager = NrtLoggerManager()
