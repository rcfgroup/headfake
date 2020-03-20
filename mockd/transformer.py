import random as rnd
from .error import ChangeValue
from .base import ParamList
import datetime as dt

class Transformer(ParamList):
    def before_next(self, field, row):
        pass

    def after_next(self, field, row, value):
        return value

class UpperCase(Transformer):
    def after_next(self, field, row, value):
        return str(value).upper()

class IntermittentBlanks(Transformer):
    def before_next(self, field, row, value):
        if rnd.random() < self.blank_probability:
            raise ChangeValue("")

class ReformatDateTime(Transformer):
    def after_next(self, field, row, value):
        source_dt = dt.datetime.strptime(value, self.source_format)
        return source_dt.strftime(self.target_format)

class ConvertStrToDate(Transformer):
    def after_next(self, field, row, value):
        source_dt = dt.datetime.strptime(value, self.format)
        return source_dt.date()

class ConvertStrToDateTime(Transformer):
    def after_next(self, field, row, value):
        source_dt = dt.datetime.strptime(value, self.format)
        source_dt = source_dt.replace(tzinfo=dt.timezone.utc)
        return source_dt