"""
This package contains the error classes raised by headfake.
"""


class ChangeValue(Exception):
    """
    Raised by a Transformer or Field when the generated value should change. The 'value' in the accessor is the new
    value.
    """

    def __init__(self, value):
        self.value = value
        super().__init__("Change value raised to " + str(self.value))
