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
        self.__stream_handler_list.append(stream_handler)

    def close_stream_handlers(self):
        for handler in self.__stream_handler_list:
            handler.close()

        self.__stream_handler_list = []

    def __verify_stream_handler_list_not_empty(self):
        if not self.__stream_handler_list:
            raise Exception(
                'Unable write to logs'
                ' if no stream handler attached to logger')


class NrtLoggerManager:
    __is_running: bool = False
    __logger_dict: dict[str, NrtLogger]

    def __init__(self):
        self.__verify_not_initiated()
        self.__logger_dict = {}

    def get_logger(self, name: str) -> NrtLogger:
        yaml_logger = self.__logger_dict.get(name)

        if yaml_logger is None:
            self.__logger_dict[name] = NrtLogger()

        return self.__logger_dict[name]

    def close_logger(self, name):
        logger = self.__logger_dict.get(name)

        if logger:
            logger.close_stream_handlers()

    @classmethod
    def __verify_not_initiated(cls):
        if cls.__is_running:
            raise Exception(
                'NrtLoggerManager should not be initiated.'
                ' Please use yaml_logging')

        cls.__is_running = True


logger_manager = NrtLoggerManager()
