"""
This package contains the error classes raised by headfake.
"""


class TransformationError(Exception):
    """
    Raised by a Transformer or Field when there is an issue with the transformation.
    """
    def __init__(self, field, transformer, row, orig_exception):
        super().__init__(f"Error transforming '{field.name}' value. Transformer: '{transformer.__class__}'; data:{row}; Original error:{orig_exception.__class__.__name__} ({orig_exception})")