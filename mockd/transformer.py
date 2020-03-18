import random as rnd
from .error import ChangeValue
from .base import ParamList

class Transformer(ParamList):
    def init_params(self, field):
        pass

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