import unittest

from nrt_logging.exceptions import NotImplementedCodeException


class NotImplementedCodeExceptionTests(unittest.TestCase):
    def test_raise_exception_without_message(self):
        with self.assertRaises(
                NotImplementedCodeException, msg='Bug: Not implemented code'):
            raise NotImplementedCodeException()

    def test_raise_exception_with_message(self):
        msg = '1234'

        with self.assertRaises(
                NotImplementedCodeException, msg=msg):
            raise NotImplementedCodeException(msg=msg)


if __name__ == '__main__':
    unittest.main()
