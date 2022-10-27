import os

import nrt_logging
from nrt_logging.test.tests_suite import TestsSuite

PATH = os.path.dirname(__file__)


def __replace_pyproject_version():
    with open(os.path.join(PATH, 'pyproject.toml')) as f:
        file_lines = [line.strip() for line in f.readlines()]

    is_replace = False
    for i, line in enumerate(file_lines):
        if line.startswith('version'):
            version = line.split('=')[1]
            if version != nrt_logging.__version__:
                is_replace = True
                file_lines[i] = f"version='{nrt_logging.__version__}'"

    if is_replace:
        with open(os.path.join(PATH, 'pyproject.toml'), 'w') as f:
            f.write('\n'.join(file_lines))


##################################################################

__replace_pyproject_version()

test_suite = TestsSuite(True)
test_suite.run_tests()
test_suite.create_report()
test_suite.erase_data()
