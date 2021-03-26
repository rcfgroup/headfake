"""
Fake/mock field generation logic
"""

import csv
import random as rnd
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

import attr
import faker

from headfake.error import ChangeValue
from headfake.fieldset import Fieldset
from headfake.transformer import Transformer
from headfake.util import create_package_class, calculate_age, locate_file

LOCALE = "en_GB"

@attr.s(kw_only=True)
class Field(ABC):
    """
    Basic field class. This uses the attrs module to handle available/required class attributes/defaults.
    The key properties are 'transformers' which is a list of transformer class instances which will act upon the values
    at various points and 'name' which is the field name (this can be None where it is not needed).
    """
    transformers:List[Transformer] = attr.ib(factory=list)
    name:Optional[str] = attr.ib(default=uuid.uuid4())

    def after_init_params(self):
        [t.init_params(self) for t in self.transformers]

    @property
    def names(self):
        return [self.name]

    def init_params(self):
        pass

    def init_from_fieldset(self, fieldset:Fieldset):
        """
        Initialise from containing fieldset. This is often used to obtain information on other fields in the
        fieldset for later use.
        :param fieldset:
        :return:
        """
        pass

    def next_value(self, row:Dict[str,Any])->Union[Any,Dict[str,Any]]:
        """
        Get next mock value for field. Acts as a decorator on the private '_next_value' method.
        If 'transformers' have been provided in the constructor they surround the '_next_value' method by
        with 'before_next' and 'after_next' methods for each transformer.

        Any headfake.error.ChangeValue exception thrown by a transformer will be caught and the supplied value will be
        returned.

        :param row:Dict[str,Any] The current data row as a dictionary
        :return: Union[Any,Dict[str,Any]] Dictionary containing multiple fields OR a single field value

        """
        try:
            [t.before_next(self, row) for t in self.transformers]
        except ChangeValue as ex:
            return ex.value

        val = self._next_value(row)

        for t in self.transformers:
            val = t.after_next(self, row, val)

        return val

    @abstractmethod
    def _next_value(self, row:Dict[str,Any]):
        pass

@attr.s(kw_only=True)
class IdGenerator(ABC):
    """
    Base class which handles the generation of zero-padded values for ID fields.
    :param length:int Length of zero-padded ID value
    :param min_value:int Minimum value/start point for ID value (default=1)
    """
    length: int = attr.ib()
    min_value: int = attr.ib(default=1)
    name = attr.ib(default=None)

    def select_id(self):
        val = self._select_number()
        return str(val).zfill(self.length)


@attr.s(kw_only=True)
class IncrementIdGenerator(IdGenerator):
    """
    Incremental ID generator.
    """
    current_no: int = attr.ib()

    @current_no.default
    def _default_current_no(self):
        return self.min_value

    def _select_number(self):
        if len(str(self.current_no)) > self.length:
            raise ValueError("next number is greater than length")

        val = self.current_no
        self.current_no += 1

        return val


@attr.s
class RandomIdGenerator(IdGenerator):
    """
    Base random ID generator. Sets up a maximum value.
    """
    max_value: int = attr.ib()

    @max_value.default
    def _default_max_value(self):
        return int("9" * self.length)


@attr.s
class RandomNoReuseIdFieldType(RandomIdGenerator):
    """
    Random unique ID generator.
    """
    _used_values: List[id] = attr.ib(factory=list)

    def _select_number(self):
        val = rnd.randrange(self.min_value, self.max_value)
        if val in self._used_values:
            return self._select_number()

        self._used_values.append(val)

        return val


@attr.s
class RandomReuseIdFieldType(RandomIdGenerator):
    """
    Random non-unique ID generator.
    """
    _used_values: List[id] = attr.ib(factory=list)

    def _select_number(self):
        val = rnd.randrange(self.min_value, self.max_value)
        return str(val).zfill(self.length)


@attr.s(kw_only=True)
class IdField(Field):
    """
    Field which generates ID values with prefix and suffix based on the supplied 'generator' class.
    """
    prefix: str = attr.ib(default="")
    suffix: str = attr.ib(default="")
    generator: IdGenerator = attr.ib(default=IncrementIdGenerator(length=3))

    def _next_value(self, row):
        val = self.generator.select_id()

        return self.prefix + val + self.suffix


@attr.s(kw_only=True)
class FakerField(Field):
    """
    Base field for Faker-based value creation.
    """
    _fake = attr.ib()

    @_fake.default
    def _default_faker(self):
        fake = faker.Faker(LOCALE)
        return fake


@attr.s(kw_only=True)
class OptionValueField(Field):
    """
    Mock option value field, which uses a list of probabilities to determine which to pick.
    """

    probabilities = attr.ib()
    _option_picks = attr.ib()

    @_option_picks.default
    def _default_option_picks(self):
        option_picks = []

        for val, prob in self.probabilities.items():
            option_picks += [val] * int(prob * 100)

        return option_picks

    def _next_value(self, row):
        return rnd.choice(self._option_picks)


@attr.s(kw_only=True)
class DerivedField(Field):
    @abstractmethod
    def _internal_field(self):
        pass

    def __attrs_post_init__(self):
        self._internal_field = self._internal_field()

    def _next_value(self, row):
        return self._internal_field.next_value(row)

@attr.s(kw_only=True)
class ConstantField(Field):
    """
    Mock constant field. Deprecated: no longer needed - can simply use scalar value (e.g. string, number)
    """
    value = attr.ib()

    def _next_value(self, row):
        return self.value


@attr.s(kw_only=True)
class ConcatField(Field):
    """
    Concatenate multiple mock fields together
    """
    fields: List[Field] = attr.ib(factory=list)
    glue: str = attr.ib(default="")

    def _next_value(self, row):
        vals = []
        for field in self.fields:
            value = field.next_value(row)
            vals.append(value)

        return self.glue.join(vals)

    def init_from_fieldset(self, fieldset):
        for field in self.fields:
            field.init_from_fieldset(fieldset)


@attr.s(kw_only=True)
class MapFileField(Field):
    """
    Acts as focal point for random selection from a 'mapping_file'. N.B. Currently the mapping file is an absolute path
    to a file, but in future it should take into account interlinked fieldsets.

    The `key_field` has two roles:

    1. it specifies the field in the mapping file where the values in this field come from
    2. it is used as the key to lookup values when used in conjunction with one or LookupMapFileFields

    This class also acts as a store for the mapping file and has to be specified in the LookupMapFileField.
    """

    mapping_file = attr.ib()
    key_field = attr.ib()
    key_field_store = attr.ib()

    @key_field_store.default
    def _default_key_field_store(self):
        input_file = locate_file(self.mapping_file)
        with open(input_file, "r") as out:
            reader = csv.DictReader(out)
            map = {l.get(self.key_field): l for l in reader}

        return map

    def _next_value(self, row):
        rnd_key = rnd.choice(list(self.key_field_store.keys()))
        return rnd_key


@attr.s(kw_only=True)
class LookupMapFileField(Field):
    """
    Uses a specified MapFileField to get a data value for a specified column, using the key value from that field.
    """

    lookup_value_field = attr.ib()
    map_file_field = attr.ib()
    _map_file_field_obj = attr.ib(default=None)

    def _next_value(self, row):
        map_key = row.get(self._map_file_field_obj.name)
        map_line = self._map_file_field_obj.key_field_store.get(map_key)
        return map_line.get(self.lookup_value_field)

    def init_from_fieldset(self, fieldset):
        self._map_file_field_obj = fieldset.fields.get(self.map_file_field)
        first_store_row = list(self._map_file_field_obj.key_field_store.values())[0]
        if self.lookup_value_field not in first_store_row:
            raise ValueError("Lookup value field  '%s' not found in file" % self.lookup_value_field)


@attr.s(kw_only=True)
class IfElseField(Field):
    """
    Create field based on condition
    """
    condition = attr.ib()
    true = attr.ib()
    false = attr.ib()

    def _next_value(self, row):
        if self.condition.is_true(row):
            return self.true.next_value(row) if hasattr(self.true, "next_value") else self.true
        else:
            return self.false.next_value(row) if hasattr(self.false, "next_value") else self.false


@attr.s(kw_only=True)
class Condition:
    """
    Dependent field condition
    """
    field = attr.ib()  # name of field to check or field definition (e.g. could nest IfElseField)
    operator = attr.ib()
    value = attr.ib()

    def is_true(self, row):
        return self.operator(row.get(self.field),self.value)


@attr.s(kw_only=True)
class MultiField(Field):
    """
    Generate a list of fields
    """
    field: Field = attr.ib()
    min_values: int = attr.ib()
    max_values: int = attr.ib()
    glue: str = attr.ib(default=None)

    def _next_value(self, row):
        num_values = rnd.randrange(self.min_values, self.max_values)

        outputs = [self.field.next_value(row) for n in range(1,num_values+1)]

        return self.glue.join(outputs) if self.glue else outputs
