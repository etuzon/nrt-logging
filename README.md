#Hierarchical logging in yaml format.

Hierarchical logging help to group logs that related to the same code flow.

Logging fields can be in Yaml format or in Line format.

In addition to automatic hierarchy, manually hierarchy is supported.

###Example:

Example of
 - A.a1() - WARN
   - B.child_1() - INFO
     - B.child_2() - INFO

```
from nrt_logging.logger import logger_manager, NrtLogger
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum

NAME_1 = 'name 1'


class Child:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def child_1(self):
        self.__logger.info('Child 1')
        self.child_2()

    def child_2(self):
        self.__logger.info('Child 2')


class A:
    __logger: NrtLogger
    __child: Child

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__child = Child()

    def a1(self):
        self.__logger.warn('Message 1')
        self.__child.child_1()

```

## Init logger with LINE style

```
def logging_line_style():
    sh = ConsoleStreamHandler()
    sh.log_style = LogStyleEnum.LINE
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()
 
logging_line_style()
```

### Output

- log: 2022-10-13 00:22:57.676415 [WARN] [test_line_style.py.A.a1:29] Message 1
  children:
    - log: 2022-10-13 00:22:57.688419 [INFO] [test_line_style.py.Child.child_1:13] Child 1
      children:
        - log: 2022-10-13 00:22:57.700451 [INFO] [test_line_style.py.Child.child_2:17] Child 2
        
## Init logger with YAML style

```
def logging_yaml_style():
    sh = ConsoleStreamHandler()
    sh.log_style = LogStyleEnum.YAML
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    a = A()
    a.a1()

logging_yaml_style()
```

### Output

---
date: 2022-10-13 00:29:52.548451
log_level: WARN
path: test_line_style.py.A
method: a1
line_number: 31
message: Message 1
children:
  - date: 2022-10-13 00:29:52.558965
    log_level: INFO
    path: test_line_style.py.Child
    method: child_1
    line_number: 15
    message: Child 1
    children:
      - date: 2022-10-13 00:29:52.569975
        log_level: INFO
        path: test_line_style.py.Child
        method: child_2
        line_number: 19
        message: Child 2
      
## Example of changing hierarchy manually

```
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger import logger_manager
from nrt_logging.logger_stream_handlers import ConsoleStreamHandler, LogStyleEnum


sh = ConsoleStreamHandler()
sh.log_level = LogLevelEnum.TRACE
sh.log_style = LogStyleEnum.LINE
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

### Output:

- log: 2022-10-13 00:35:43.310527 [INFO] [test_manual_hierarchy_logging.py.<module>:12] main level log
  children:
    - log: 2022-10-13 00:35:43.318527 [INFO] [test_manual_hierarchy_logging.py.<module>:14] child 1
      children:
        - log: 2022-10-13 00:35:43.325527 [INFO] [test_manual_hierarchy_logging.py.<module>:16] child 1_1
    - log: 2022-10-13 00:35:43.333531 [INFO] [test_manual_hierarchy_logging.py.<module>:18] child 2
- log: 2022-10-13 00:35:43.341532 [INFO] [test_manual_hierarchy_logging.py.<module>:20] continue main level
