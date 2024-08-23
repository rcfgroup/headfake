import random as rnd
import re

import attr

from datetime import datetime as dt, timezone as tz, timedelta as td

import numpy as np

@attr.s
class Transformer:
    """
    Logic for transforming field row values. For example, changing string case, randomising insertion of errors.
    Multiple transformers can be specified for each field.
    """
    def transform(self, field, row, value):
        pass

class UpperCase(Transformer):
    """
    Converts value to upper case.
    """

    def transform(self, field, row, value):
        return str(value).upper()


@attr.s(kw_only=True)
class IntermittentBlanks(Transformer):
    """
    Adds intermittent blank_values (default="") randomly at a rate specified by the blank_probability property.
    """
    blank_probability = attr.ib()
    blank_value = attr.ib(default="")

    def transform(self, field, row, value):
        if rnd.random() < self.blank_probability:
            return self.blank_value

        return value

@attr.s(kw_only=True)
class RegexSubstitute(Transformer):
    """
    Perform a regular expression substitution
    """
    pattern = attr.ib()
    replace = attr.ib()

    def transform(self, field, row, value):
        return re.sub(self.pattern, self.replace, value)


@attr.s(kw_only=True)
class Truncate(Transformer):
    """
    Truncate a value
    """
    length = attr.ib()

    def transform(self, field, row, value):
        return value[:int(self.length)]


@attr.s(kw_only=True)
class Padding(Transformer):
    """
    Pad a value to be a given length with the specified fill character
    """
    length = attr.ib()
    fill = attr.ib()
    align = attr.ib('left')

    def transform(self, field, row, value):
        methods = {
            'left': value.ljust,
            'right': value.rjust,
        }
        pad = methods.get(self.align)
        if pad:
            return pad(self.length, str(self.fill))
        else:
            return value


@attr.s(kw_only=True)
class SplitPiece(Transformer):
    """
    Splits a string and returns a specific element of the array.

    So given a value of "A;B;C;D", "B" would be returned if a separator of ";" and index of 1 is used.

    """
    separator = attr.ib() #string to separator on
    index = attr.ib() #index of separated string to return

    def transform(self, field, row, value):
        pieces = value.split(self.separator)

        if self.index>len(pieces)-1:
            return ""

        return pieces[self.index]


@attr.s(kw_only=True)
class ReformatDateTime(Transformer):
    """
    Reformats a string date into a different format. For example it could take an ISO formatted (e.g. YYYY-MM-DD) date
    string and convert it into UK locale (e.g. DD/MM/YYYY) in a single transformation.
    """
    source_format = attr.ib()
    target_format = attr.ib()
    _error_class = ValueError

    def transform(self, field, row, value):
        source_dt = dt.strptime(value, self.source_format)
        return source_dt.strftime(self.target_format)


@attr.s(kw_only=True)
class ConvertStrToDate(Transformer):
    """
    Converts a string value with a specified date 'format' into a date object
    """
    format = attr.ib()
    _error_class = ValueError

    def transform(self, field, row, value):
        source_dt = dt.strptime(value, self.format)
        return source_dt.date()

@attr.s(kw_only=True)
class FormatDateTime(Transformer):
    """
    Formats a date/datetime object as a string with the specified date/datetime 'format'.
    """
    format = attr.ib()
    _error_class = ValueError

    def transform(self, field, row, value):
        return value.strftime(self.format)


@attr.s(kw_only=True)
class ConvertStrToDateTime(Transformer):
    """
    Converts a string value with a specified datetime 'format' into a datetime object
    """
    format = attr.ib()
    _error_class = ValueError

    def transform(self, field, row, value):
        source_dt = dt.strptime(value, self.format)
        source_dt = source_dt.replace(tzinfo=tz.utc)
        return source_dt

@attr.s(kw_only=True)
class ConvertToNumber(Transformer):
    """
    Converts a value into an number. If the value is not a number, returns None.
    Can specify whether it is returned as an integer (as_integer) or not
    """
    as_integer = attr.ib(default=None)
    _error_class = TypeError

    def transform(self, field, row, value):
        return int(value) if self.as_integer else np.float32(value)
import logging

@attr.s(kw_only=True)
class FormatNumber(Transformer):
    """
    Formats number using the specified number of decimal places (dp) and returns as a string.
    If the value is not a number, returns None.
    """
    dp = attr.ib(default=None)
    _error_class = ValueError

    def transform(self, field, row, value):
        fstring = "{:0." + str(self.dp) + "f}"
        return fstring.format(value)


@attr.s(kw_only=True)
class ConvertToDaysDelta(Transformer):
    """
    Converts a value into a timedelta object. If the value is not a number, returns None.
    """
    error_value = attr.ib(default=None)
    _error_class = TypeError

    def transform(self, field, row, value):
        return td(days=value)


@attr.s(kw_only=True)
class GetProperty(Transformer):
    """
    Get a property from the object created during value generation.
    For example to get the number of days from a timedelta object you could use the **prop_name** 'days'.

    If the attribute does not exist, return the value specified in 'default' (None by default).
    """
    prop_name = attr.ib()
    _error_class = AttributeError

    def transform(self, field, row, value):
        return getattr(value, self.prop_name)

