from typing import Optional

from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_stream_handlers import \
    LoggerStreamHandlerBase, ManualDepthEnum, DEFAULT_LOG_LEVEL


class NrtLogger:
    """
    Hierarchical logger.
    Method logs that were called by other methods
    will be children of the 'parents' methods logs.

    Logger element can be in yaml style,
    meaning each field will be separated by yaml element,
    or it can be in line style with children logs of children methods.

    User can force logs to be children of previous logs in the same method.
    """

    __stream_handler_list: list[LoggerStreamHandlerBase]
    __log_level: Optional[LogLevelEnum] = None

    __is_debug: bool = False

    def __init__(self, log_level: LogLevelEnum = DEFAULT_LOG_LEVEL):
        """
        Constractor.

        @param log_level:
            Logger log_level.
            Stream Handlers log method will be called
            only if logger log >= log_level.
        """

        self.__log_level = log_level
        self.__stream_handler_list = []

    def critical(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.CRITICAL:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.critical(msg, manual_depth)

    def error(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.ERROR:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.error(msg, manual_depth)

    def warn(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.WARN:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.warn(msg, manual_depth)

    def info(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.INFO:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.info(msg, manual_depth)

    def debug(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.DEBUG:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.debug(msg, manual_depth)

    def trace(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):

        if self.log_level <= LogLevelEnum.TRACE:
            self.__verify_stream_handler_list_not_empty()

            for handler in self.__stream_handler_list:
                handler.trace(msg, manual_depth)

    def increase_depth(self):
        for handler in self.__stream_handler_list:
            handler.increase_depth()

    def decrease_depth(self, level: int = 1):
        for handler in self.__stream_handler_list:
            handler.decrease_depth(level)

    def add_stream_handler(
            self,
            stream_handler: LoggerStreamHandlerBase,
            is_min_sh_logger_level: bool = True):
        """
        Add Stream Handler.

        @param stream_handler:
        @param is_min_sh_logger_level:
            Logger log level is minimum of
            logger log level and stream handler log level.
        @return:
        """

        if self.is_debug:
            stream_handler.is_debug = self.is_debug

        if is_min_sh_logger_level:
            self.log_level = min(self.__log_level, stream_handler.log_level)

        self.__stream_handler_list.append(stream_handler)

    def close_stream_handlers(self):
        for handler in self.__stream_handler_list:
            handler.close()

        self.__stream_handler_list = []

    def update_log_level(
            self, log_level: LogLevelEnum, is_update_sh: bool = True):

        self.__log_level = log_level

        if is_update_sh:
            self.__update_stream_handlers_log_level(log_level)

    @property
    def log_level(self) -> LogLevelEnum:
        return self.__log_level

    @log_level.setter
    def log_level(self, log_level: LogLevelEnum):
        self.__log_level = log_level

    @property
    def is_debug(self) -> bool:
        return self.__is_debug

    @is_debug.setter
    def is_debug(self, is_debug: bool):
        self.__is_debug = is_debug

    def __update_stream_handlers_log_level(self, log_level: LogLevelEnum):
        for sh in self.__stream_handler_list:
            sh.log_level = log_level

    def __verify_stream_handler_list_not_empty(self):
        if not self.__stream_handler_list:
            raise RuntimeError(
                'Unable write to logs'
                ' if no stream handler attached to logger')
