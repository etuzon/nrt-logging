# Hierarchical logging in yaml format.

Hierarchical logging help to group logs that are related to the same code flow.

Log style can be styled in Yaml format or in Line format.

### Examples:

#### Output in YAML style

```Python
from examples.demo_classes.demo_classes import NAME_1, A
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


def logging_line_style():
    sh = ConsoleStreamHandler()
    sh.style = LogStyleEnum.LINE
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()


def logging_yaml_style():
    sh = ConsoleStreamHandler()
    sh.style = LogStyleEnum.YAML
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()


logging_yaml_style()
```

Output
```YAML
---
date: 2022-10-21 21:20:49.658272
log_level: WARN
path: demo_classes.py.A
method: a1
line_number: 32
message: Message 1
children:
  - date: 2022-10-21 21:20:49.666366
    log_level: INFO
    path: demo_classes.py.Child
    method: child_1
    line_number: 16
    message: Child 1
    children:
      - date: 2022-10-21 21:20:49.675316
        log_level: INFO
        path: demo_classes.py.Child
        method: child_2
        line_number: 20
        message: Child 2
```

#### Output in LINE style

```Python
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


sh = ConsoleStreamHandler()
sh.log_level = LogLevelEnum.TRACE
sh.style = LogStyleEnum.LINE
logger = logger_manager.get_logger('NAME_1')
logger.add_stream_handler(sh)

logger.info('main level log')
logger.increase_depth()
logger.info('child 1')
logger.increase_depth()
logger.info('child 1_1')
logger.decrease_depth()
logger.info('child 2')
logger.decrease_depth()
logger.info('continue main level')
```

Output
```YAML
- log: 2022-10-21 21:30:16.361425 [INFO] [manual_hierarchy_line_logging.py.<module>:13] main level log
  children:
    - log: 2022-10-21 21:30:16.367386 [INFO] [manual_hierarchy_line_logging.py.<module>:15] child 1
      children:
        - log: 2022-10-21 21:30:16.373975 [INFO] [manual_hierarchy_line_logging.py.<module>:17] child 1_1
    - log: 2022-10-21 21:30:16.380979 [INFO] [manual_hierarchy_line_logging.py.<module>:19] child 2
- log: 2022-10-21 21:30:16.387013 [INFO] [manual_hierarchy_line_logging.py.<module>:21] continue main level
```

### Config file

log_manager config file in YAML style.<br>
Configure loggers and stream handlers.

parameters are inherited. Parameters that are deeper in YAML file will be taken.

```YAML
log_level: WARN
date_format: '%Y-%m-%d %H:%M:%S'
loggers:
  - name: TEST1
    style: yaml
    log_line_template: '[$log_level$] <$date$> $message$'
    stream_handlers:
      - type: console
        style: line
      - type: file
        file_path: logs/log_test_1.txt
        log_level: DEBUG
        style: line
        date_format: '%Y'
        log_line_template: 'Test1 $date$ $message$'
  - name: TEST2
    style: yaml
    stream_handlers:
      - type: file
        file_path: logs/log_test_2.txt
        log_level: ERROR
        date_format: '%Y'
        log_yaml_elements:
          ['log_level', 'date', 'message']
```

```Python
from examples.demo_classes.demo_classes import \
    NAME_1, A, NAME_2
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum

CONFIG_FILE_PATH = './config/config1.yaml'

logger_manager.set_config(file_path=CONFIG_FILE_PATH)
```

Wiki: https://github.com/etuzon/Python-NRT-Logging/wiki/NRT-Logging

