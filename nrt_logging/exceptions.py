from typing import Optional


class NotImplementedCodeException(Exception):
    def __init__(self, msg: Optional[str] = None):
        if msg is None:
            msg = 'Bug: Not implemented code'

        super().__init__(msg)
