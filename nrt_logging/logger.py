from nrt_logging.logger_stream_handlers import \
    LoggerStreamHandlerBase, ManualDepthEnum


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

    __is_debug: bool = False

    def __init__(self):
        self.__stream_handler_list = []

    def critical(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.critical(msg, manual_depth)

    def error(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.error(msg, manual_depth)

    def warn(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.warn(msg, manual_depth)

    def info(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.info(msg, manual_depth)

    def debug(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.debug(msg, manual_depth)

    def trace(
            self,
            msg: str,
            manual_depth: ManualDepthEnum = ManualDepthEnum.NO_CHANGE):
        self.__verify_stream_handler_list_not_empty()

        for handler in self.__stream_handler_list:
            handler.trace(msg, manual_depth)

    def increase_depth(self):
        for handler in self.__stream_handler_list:
            handler.increase_depth()

    def decrease_depth(self, level: int = 1):
        for handler in self.__stream_handler_list:
            handler.decrease_depth(level)

    def add_stream_handler(self, stream_handler: LoggerStreamHandlerBase):
        if self.is_debug:
            stream_handler.is_debug = self.is_debug

        self.__stream_handler_list.append(stream_handler)

    def close_stream_handlers(self):
        for handler in self.__stream_handler_list:
            handler.close()

        self.__stream_handler_list = []

    @property
    def is_debug(self) -> bool:
        return self.__is_debug

    @is_debug.setter
    def is_debug(self, is_debug: bool):
        self.__is_debug = is_debug

    def __verify_stream_handler_list_not_empty(self):
        if not self.__stream_handler_list:
            raise RuntimeError(
                'Unable write to logs'
                ' if no stream handler attached to logger')
