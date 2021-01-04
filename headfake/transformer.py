import random as rnd
import re
import uuid

import attr

from .error import ChangeValue


@attr.s
class Transformer:
    """
    Logic for transforming field row values. For example, changing string case, randomising insertion of errors.
    Multiple transformers can be specified for each field.
    """
    name = attr.ib(default=uuid.uuid4())

    def before_next(self, field, row):
        """
        Transformation before the value is obtained.

        Throw a headfake.error.ChangeValue exception with a new value if you want the value to be changed up the stack.
        :param field:
        :param row:
        :return:
        """
        pass

    def after_next(self, field, row, value):
        return value


class UpperCase(Transformer):
    """
    Converts value to upper case.
    """
    def after_next(self, field, row, value):
        return str(value).upper()


@attr.s(kw_only=True)
class IntermittentBlanks(Transformer):
    """
    Adds intermittent blank_values (default="") randomly at a rate specified by the blank_probability property.
    """
    blank_probability = attr.ib()
    blank_value = attr.ib(default="")

    def before_next(self, field, row, value):
        if rnd.random() < self.blank_probability:
            raise ChangeValue(self.blank_value)


@attr.s(kw_only=True)
class RegexSubstitute(Transformer):
    """
    Perform a regular expression substitution
    """
    pattern = attr.ib()
    replace = attr.ib()

    def after_next(self, field, row, value):
        return re.sub(self.pattern, self.replace, value)

@attr.s(kw_only=True)
class Truncate(Transformer):
    """
    Truncate a value
    """
    length = attr.ib()

    def after_next(self, field, row, value):
        return value[:int(self.length)]


@attr.s(kw_only=True)
class Padding(Transformer):
    """
    Pad a value to be a given length with the specified fill character
    """
    length = attr.ib()
    fill = attr.ib()
    align = attr.ib('left')

    def after_next(self, field, row, value):
        methods = {
            'left': value.ljust,
            'right': value.rjust,
        }
        pad = methods.get(self.align)
        if pad:
            return pad(self.length, str(self.fill))
        else:
            return value

