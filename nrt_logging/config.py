from enum import Enum
from typing import Optional

import yaml
import schema

from nrt_logging.exceptions import NotImplementedCodeException
from nrt_logging.log_format import LogElementEnum
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_stream_handlers import \
    LogStyleEnum, StreamHandlerEnum, ConsoleStreamHandler, \
    FileStreamHandler, LoggerStreamHandlerBase


class FileSizeEnum(Enum):
    B = 1
    KB = 10 ** 3
    MB = 10 ** 6
    GB = 10 ** 9
    TB = 10 ** 12

    @property
    def bytes(self) -> int:
        return self._value_

    @classmethod
    def build(cls, name: str):
        name_u = name.upper()

        for file_size_enum in cls:
            if name_u == file_size_enum.name:
                return file_size_enum

        raise ValueError(f'[{name}] is not valid file size name')

    @classmethod
    def get_bytes(cls, file_size_str: str) -> int:
        if ' ' in file_size_str:
            return cls.__get_bytes_for_str_with_space(file_size_str)

        return cls.__get_bytes_for_str_without_space(file_size_str)

    @classmethod
    def __get_bytes_for_str_with_space(cls, file_size_str: str) -> int:
        file_size_split = file_size_str.split(' ')

        if len(file_size_split) != 2:
            raise ValueError(
                f'File size [{file_size_str}] is with invalid syntax')

        num = int(file_size_split[0])

        if num <= 0:
            raise ValueError(
                f'File size [{file_size_str}] has invalid syntax')

        return num * cls.build(file_size_split[1]).bytes

    @classmethod
    def __get_bytes_for_str_without_space(cls, file_size_str: str) -> int:
        if len(file_size_str) > 2:
            try:
                file_size = FileSizeEnum.build(file_size_str[-2:])
                num = cls.__num_str_to_int(
                    file_size_str[:-2], file_size_str)
                return num * file_size.bytes
            except ValueError:
                pass

        if len(file_size_str) >= 2:
            file_size = FileSizeEnum.build(file_size_str[-1:])
            num = cls.__num_str_to_int(
                file_size_str[:-1], file_size_str)
            return num * file_size.bytes

        raise ValueError(
            f'File size [{file_size_str}] has invalid syntax')

    @classmethod
    def __num_str_to_int(cls, num_str: str, s: str):
        if not num_str.isnumeric():
            raise ValueError(f'File size [{s}] has invalid syntax')

        num = int(num_str)

        if num <= 0:
            raise ValueError(f'File size [{s}] has invalid syntax')

        return num


class ConfigBase:
    FILE_SIZE_UNIT = \
        {'B': 1, 'KB': 10 ** 3, 'MB': 10 ** 6, 'GB': 10 ** 9, 'TB': 10 ** 12}

    DEFAULT_FILE_SIZE_LIMITATION = 10 * FileSizeEnum.MB.bytes
    DEFAULT_FILES_AMOUNT = 10

    DEBUG = 'debug'
    LOG_LEVEL = 'log_level'
    STYLE = 'style'
    DATE_FORMAT = 'date_format'
    LOG_LINE_TEMPLATE = 'log_line_template'
    LOG_YAML_ELEMENTS = 'log_yaml_elements'
    IS_LIMIT_FILE_SIZE = 'limit_file_size'
    FILE_SIZE_LIMITATION = 'file_size'
    FILES_AMOUNT = 'files_amount'
    IS_ZIP = 'zip'

    _log_level: Optional[LogLevelEnum] = None
    _style: Optional[LogStyleEnum] = None
    _date_format: Optional[str] = None
    _log_line_template: Optional[str] = None
    _log_yaml_elements: Optional[list[LogElementEnum]] = None

    _is_limit_file_size: bool = False
    _file_size_limitation: int = DEFAULT_FILE_SIZE_LIMITATION
    _files_amount: int = DEFAULT_FILES_AMOUNT
    _is_zip: bool = False

    _config: Optional[dict] = None

    _is_debug: bool = False

    def __init__(self, config: dict, is_parent_debug: bool):
        self._config = config
        self._update_is_debug(is_parent_debug)
        self._update_log_level()
        self._update_log_style()
        self._update_date_format()
        self._update_log_line_template()
        self._update_is_limit_file_size()
        self._update_file_size_limitation()
        self._update_files_amount()
        self._update_is_zip()

    @property
    def log_level(self) -> LogLevelEnum:
        return self._log_level

    @property
    def style(self) -> LogStyleEnum:
        return self._style

    @property
    def date_format(self) -> str:
        return self._date_format

    @property
    def log_line_template(self) -> str:
        return self._log_line_template

    @property
    def log_yaml_elements(self) -> Optional[list[LogElementEnum]]:
        return self._log_yaml_elements

    @property
    def is_limit_file_size(self) -> bool:
        return self._is_limit_file_size

    @property
    def file_size_limitation(self) -> int:
        return self._file_size_limitation

    @property
    def files_amount(self) -> int:
        return self._files_amount

    @property
    def is_zip(self) -> bool:
        return self._is_zip

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    def _update_is_debug(self, is_parent_debug: bool):
        is_debug = self._config.get(self.DEBUG)

        if is_debug is None:
            is_debug = is_parent_debug

        self._is_debug = bool(is_debug)

    def _update_log_level(self):
        log_level_str = self._config.get(self.LOG_LEVEL)

        if log_level_str:
            try:
                self._log_level = LogLevelEnum.build(log_level_str)
            except ValueError:
                raise ValueError(
                    f'{self.LOG_LEVEL} value [{log_level_str}]'
                    f' in log config is invalid')

    def _update_log_style(self):
        log_style_str = self._config.get(self.STYLE)

        if log_style_str:
            try:
                self._style = LogStyleEnum.build_by_name(log_style_str)
            except ValueError:
                raise ValueError(
                    f'{self.STYLE} value [{log_style_str}]'
                    f' in log config is invalid')

    def _update_date_format(self):
        self._date_format = self._config.get(self.DATE_FORMAT)

    def _update_log_line_template(self):
        self._log_line_template = self._config.get(self.LOG_LINE_TEMPLATE)

    def _update_log_element_list(self):
        log_element_enum_list = []

        log_element_str_list = self._config.get(self.LOG_YAML_ELEMENTS)

        if log_element_str_list:
            for log_element_str in log_element_str_list:
                try:
                    log_element_enum = LogElementEnum.build(log_element_str)
                    log_element_enum_list.append(log_element_enum)
                except ValueError:
                    raise ValueError(
                        f'Element [{log_element_str}] in logger config file'
                        f' is not valid YAML log element name')

            self._log_yaml_elements = log_element_enum_list

    def _update_is_limit_file_size(self):
        self._is_limit_file_size = \
            bool(self._config.get(self.IS_LIMIT_FILE_SIZE))

    def _update_file_size_limitation(self):
        file_size_str = self._config.get(self.FILE_SIZE_LIMITATION)

        if file_size_str:
            self._file_size_limitation = FileSizeEnum.get_bytes(file_size_str)

    def _update_files_amount(self):
        files_amount_str = self._config.get(self.FILES_AMOUNT)

        if files_amount_str is not None:
            self._files_amount = int(files_amount_str)

            if self._files_amount < 0:
                raise ValueError(
                    'Files amount in logger confile file cannot be negative')

    def _update_is_zip(self):
        is_zip = self._config.get(self.IS_ZIP)

        if is_zip is not None:
            self._is_zip = is_zip


class StreamHandlerConfig(ConfigBase):
    STREAM_HANDLER_NAME = 'name'
    TYPE = 'type'
    FILE_PATH = 'file_path'

    __name: Optional[str] = None
    __type: Optional[StreamHandlerEnum] = None
    __file_path: Optional[str] = None

    def __init__(self, config: dict, is_parent_debug: bool):
        super().__init__(config, is_parent_debug)
        self.__update_stream_handler_name()
        self.__update_type()
        self._update_log_element_list()
        self.__update_file_path()

    def build_stream_handler(self) -> LoggerStreamHandlerBase:
        if self.type == StreamHandlerEnum.CONSOLE:
            return ConsoleStreamHandler()

        if self.type == StreamHandlerEnum.FILE:
            return FileStreamHandler(self.file_path)

        raise NotImplementedCodeException(
            'Bug: Not implemented stream handler from config'
            f' for type [{self.type.name}]')

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> StreamHandlerEnum:
        return self.__type

    @property
    def file_path(self) -> str:
        return self.__file_path

    def __update_type(self):
        sh_type = self._config.get(self.TYPE)

        if not sh_type:
            raise ValueError(
                'Stream handler in log config not contain type')

        try:
            self.__type = StreamHandlerEnum(sh_type)
        except ValueError:
            raise ValueError(
                f'{self.TYPE} value [{sh_type}]'
                f' in stream handler in log config is invalid')

    def __update_stream_handler_name(self):
        self.__name = self._config.get(self.STREAM_HANDLER_NAME)

    def __update_file_path(self):
        file_path = self._config.get(self.FILE_PATH)

        if not file_path and self.type == StreamHandlerEnum.FILE:
            raise ValueError(
                'file stream handler not contain'
                f' {self.FILE_PATH} in log config')

        self.__file_path = file_path


class LoggerConfig(ConfigBase):
    LOGGER_NAME = 'name'
    STREAM_HANDLERS = 'stream_handlers'

    __name: Optional[str] = None
    __stream_handler_list: Optional[list[StreamHandlerConfig]] = None

    __is_debug: bool = False

    def __init__(self, config: dict, is_parent_debug: bool):
        super().__init__(config, is_parent_debug)
        self.__update_logger_name()
        self._update_log_element_list()
        self.__update_stream_handlers()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def stream_handler_list(self) -> list[StreamHandlerConfig]:
        return self.__stream_handler_list

    @property
    def is_debug(self) -> bool:
        return self.__is_debug

    def __update_logger_name(self):
        self.__name = self._config.get(self.LOGGER_NAME)

    def __update_stream_handlers(self):
        stream_handlers_list = self._config.get(self.STREAM_HANDLERS)

        if self.__stream_handler_list is None:
            self.__stream_handler_list = []

        for stream_handler in stream_handlers_list:
            self.__stream_handler_list.append(
                StreamHandlerConfig(stream_handler, self.is_debug))


class LoggerManagerConfig(ConfigBase):
    LOGGERS_CONFIG = 'loggers'

    __loggers_config: Optional[dict[str, LoggerConfig]] = None

    def __init__(self, file_path: str = None, config: dict = None):
        self.__validate_input_parameters(file_path, config)
        self.__update_config_dict(file_path, config)
        self.__validate_schema(self._config)
        super().__init__(self._config, False)
        self._update_log_element_list()
        self.__update_loggers_config()

    @property
    def loggers_config(self) -> dict[str, LoggerConfig]:
        return self.__loggers_config

    def __update_loggers_config(self):

        self.__loggers_config = {}

        loggers_config_list = self._config.get(self.LOGGERS_CONFIG)

        if loggers_config_list is not None:
            for logger_config in loggers_config_list:
                logger_config = LoggerConfig(logger_config, self.is_debug)

                if self.loggers_config.get(logger_config.name):
                    raise ValueError(
                        f'Logger [{logger_config.name}]'
                        f' is configured multiple times in log config')

                self.loggers_config[logger_config.name] = logger_config

    def __update_config_dict(
            self, file_path: str = None, config: dict = None):

        if file_path:
            with open(file_path, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = config

    @classmethod
    def __validate_input_parameters(
            cls, file_path: str = None, config: dict = None):
        if not file_path and not config:
            raise ValueError('file_path or config parameters must be set')

        if file_path and config:
            raise ValueError(
                'file_path or config parameters must be set,'
                ' but not both of the parameters')

    @classmethod
    def __validate_schema(cls, config: dict):
        template = \
            {
                schema.Optional(cls.DEBUG): bool,
                schema.Optional(cls.LOG_LEVEL): str,
                schema.Optional(cls.STYLE): str,
                schema.Optional(cls.DATE_FORMAT): str,
                schema.Optional(cls.LOG_LINE_TEMPLATE): str,
                schema.Optional(cls.LOG_YAML_ELEMENTS): list,
                schema.Optional(StreamHandlerConfig.IS_LIMIT_FILE_SIZE): bool,
                schema.Optional(
                    StreamHandlerConfig.FILE_SIZE_LIMITATION): str,
                schema.Optional(StreamHandlerConfig.FILES_AMOUNT): int,
                schema.Optional(StreamHandlerConfig.IS_ZIP): bool,
                cls.LOGGERS_CONFIG: [
                    {
                        LoggerConfig.LOGGER_NAME: str,
                        schema.Optional(cls.DEBUG): bool,
                        schema.Optional(cls.LOG_LEVEL): str,
                        schema.Optional(cls.STYLE): str,
                        schema.Optional(cls.DATE_FORMAT): str,
                        schema.Optional(cls.LOG_LINE_TEMPLATE): str,
                        schema.Optional(cls.LOG_YAML_ELEMENTS): list[str],
                        schema.Optional(
                            StreamHandlerConfig.IS_LIMIT_FILE_SIZE): bool,
                        schema.Optional(
                            StreamHandlerConfig.FILE_SIZE_LIMITATION): str,
                        schema.Optional(
                            StreamHandlerConfig.FILES_AMOUNT): int,
                        schema.Optional(StreamHandlerConfig.IS_ZIP): bool,
                        LoggerConfig.STREAM_HANDLERS: [
                            {
                                StreamHandlerConfig.TYPE: str,
                                schema.Optional(
                                    StreamHandlerConfig
                                    .STREAM_HANDLER_NAME): str,
                                schema.Optional(
                                    StreamHandlerConfig.FILE_PATH): str,
                                schema.Optional(
                                    StreamHandlerConfig
                                    .IS_LIMIT_FILE_SIZE): bool,
                                schema.Optional(
                                    StreamHandlerConfig
                                    .FILE_SIZE_LIMITATION): str,
                                schema.Optional(
                                    StreamHandlerConfig.FILES_AMOUNT): int,
                                schema.Optional(
                                    StreamHandlerConfig.IS_ZIP): bool,
                                schema.Optional(cls.DEBUG): bool,
                                schema.Optional(cls.LOG_LEVEL): str,
                                schema.Optional(cls.STYLE): str,
                                schema.Optional(cls.DATE_FORMAT): str,
                                schema.Optional(cls.LOG_LINE_TEMPLATE): str,
                                schema.Optional(
                                    cls.LOG_YAML_ELEMENTS): list[str]
                            }
                        ]
                     }
                ]
            }

        config_schema = schema.Schema(template)
        try:
            config_schema.validate(config)
        except schema.SchemaError as se:
            error = \
                'Config file is invalid.\n'\
                'Current config:\n'\
                f'{config}\n\n'\
                'Errors:\n'\
                f'{se.code}'
            raise ValueError(error)
