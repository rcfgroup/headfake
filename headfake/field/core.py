"""
Fake/mock field generation logic
"""
__export__ = ["Field"]

import csv
import random as rnd
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime as dt, timedelta as td
import datetime

import attr
import faker

from headfake.error import ChangeValue
from headfake.transformer import Transformer
from headfake.util import create_package_class, locate_file, handle_missing_keyword, new_field_name

import numpy as np

@attr.s(kw_only=True)
class Field(ABC):
    """Acts as abstract Field class.

    Fields use the attrs module to handle available/required class attributes/defaults.

    Args:
        transformers (list): Optional list of transformer objects which act upon on field values at various points.
        name (str): Optional name of field (defaults to UUID4 string)

    """
    transformers: List[Transformer] = attr.ib(factory=list)
    name: Optional[str] = attr.ib(default=new_field_name())
    generate_after = False # force the value to be generated after other field values have been generated

    def after_init_params(self):
        [t.init_params(self) for t in self.transformers]

    def init_params(self):
        pass

    def init_from_fieldset(self, fieldset: "headfake.Fieldset"):
        """Initialises field in fieldset.

        This is run once all fields have been setup. It is generally used by fields in the fieldset to obtain
        information from other fields in the fieldset for later use.

        Args:
            fieldset: Fieldset to initialise from

        Returns:
            None
        """
        pass

    def next_value(self, row: Dict[str, Any]) -> Union[Any, Dict[str, Any]]:
        """Gets next generated value for field.

        Acts as a decorator around the private '_next_value' method.
        If 'transformers' have been provided in the constructor they can act on the value before or after it has been
        generated.

        Any headfake.error.ChangeValue exception thrown by a transformer will be caught and the supplied value will be
        returned.

        Args:
            row: The current data row as a dictionary

        Returns:
            Dictionary containing multiple fields OR a single field value

        """
        try:
            [t.before_next(self, row) for t in self.transformers]
        except ChangeValue as ex:
            return ex.value

        val = self._next_value(row)

        try:
            for t in self.transformers:
                val = t.after_next(self, row, val)
        except ChangeValue as ex:
            return ex.value

        return val

    @abstractmethod
    def _next_value(self, row: Dict[str, Any]):
        """Internal method that should be over-ridden in inheriting Field classes.

        It provides the generated next value.

        Args:
            row: The current data row as a dictionary

        Returns:
            Dictionary containing multiple fields OR a single field value
        """
        pass


@attr.s(kw_only=True)
class FakerField(Field):
    """Abstract base field for Faker-based value creation.
    """
    _fake = attr.ib()

    @_fake.default
    def _default_faker(self):
        from headfake import HeadFake
        fake = faker.Faker(HeadFake.locale)
        return fake


@attr.s(kw_only=True)
class OptionValueField(Field):
    """Field to generate option values, based on a provided dictionary of probabilities.

    Attributes:
        probabilities (dict): Dictionary of values/probabilities (e.g. {"A":0.2,"B":0.8})

    Raises:
        ValueError: when probabilities do not add up to 1
    """

    probabilities = attr.ib()
    _option_picks = attr.ib()

    @_option_picks.default
    def _default_option_picks(self):
        option_picks = []
        probs = [np.float32(prob) for prob in self.probabilities.values()]
        tot = np.sum(probs)

        if tot != 1:
            raise ValueError("Probabilities provided do not add up to 1")

        min_prob = min(self.probabilities.values())
        max_dp = count_decimal_places(min_prob)

        if max_dp>5:
            warnings.warn("Options include probabilities of 1e-" + str(max_dp) + ". This requires the creation of 1e" + str(max_dp) + " possible options")

        for val, prob in self.probabilities.items():
            num_picks = int((pow(10, max_dp)) * prob)
            option_picks += [val] * num_picks

        return option_picks

    def _next_value(self, row):
        return rnd.choice(self._option_picks)

import re
from locale import localeconv

import warnings

def count_decimal_places(value):
    value = str(value)
    dec_pt = localeconv()['decimal_point']
    decrgx = re.compile("\d+(%s\d+)?e(-)(\d+)" % dec_pt)
    find_e_value = decrgx.match(value)
    if find_e_value:
        return int(find_e_value.group(3))
    else:
        return len(value.split(dec_pt)[-1])

@attr.s(kw_only=True)
class DerivedField(Field):
    """Base field which uses an existing field type (_internal_field) to generate values.

    The class can be extended with new properties which can be used to setup the _internal_field.
    """
    @abstractmethod
    def _internal_field(self):
        pass

    def __attrs_post_init__(self):
        try:
            self._internal_field = self._internal_field()
        except TypeError as ex:
            handle_missing_keyword(ex)

    def _next_value(self, row):
        return self._internal_field.next_value(row)


@attr.s(kw_only=True)
class ConstantField(Field):
    """Field which generates constant values.

    Deprecated: can simply use scalar value (e.g. string, number)
    """
    value = attr.ib()

    def _next_value(self, row):
        return self.value


@attr.s(kw_only=True)
class ConcatField(Field):
    """
    Field which concatenates values generated by multiple fields together.

    You can also provide an optional glue string.
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
    Field which provides randomised file lookup based on a particular field.

    On initialisation this loads a CSV-based mapping file and randomises the rows based on a particular 'key_field'.
    It is then used in conjuction with one or more LookupMapFileFields to lookup values in other fields in the mapping
    file.
    """

    mapping_file = attr.ib()
    key_field = attr.ib()
    key_field_store = attr.ib()

    @key_field_store.default
    def _default_key_field_store(self):
        input_file = locate_file(self.mapping_file)
        with open(input_file, "r") as out:
            reader = csv.DictReader(out)
            data_map = {l.get(self.key_field): l for l in reader}

        return data_map

    def _next_value(self, row):
        rnd_key = rnd.choice(list(self.key_field_store.keys()))
        return rnd_key


@attr.s(kw_only=True)
class LookupMapFileField(Field):
    """
    Field which works with a specified MapFileField to get a data value from a specified column, using the key value from
    that field.
    """

    lookup_value_field = attr.ib()
    map_file_field = attr.ib()
    _map_file_field_obj = attr.ib(default=None)
    generate_after = True

    def _next_value(self, row):
        map_key = row.get(self._map_file_field_obj.name)
        map_line = self._map_file_field_obj.key_field_store.get(map_key)
        return map_line.get(self.lookup_value_field)

    def init_from_fieldset(self, fieldset):
        self._map_file_field_obj = fieldset.field_map.get(self.map_file_field)
        first_store_row = list(self._map_file_field_obj.key_field_store.values())[0]
        if self.lookup_value_field not in first_store_row:
            raise ValueError("Lookup value field  '%s' not found in file" % self.lookup_value_field)


@attr.s(kw_only=True)
class IfElseField(Field):
    """
    Field which generates a value based on the results of a condition.

    If the result is true, the true_value is generated/returned and if false, the false_value is generated.
    The true and false values can be field definitions or scalar values (e.g. strings, numbers, dates).


    """
    condition = attr.ib()
    true_value = attr.ib()
    false_value = attr.ib()
    _cond_obj = attr.ib()

    @_cond_obj.default
    def _default_cond_obj(self):
        return self.condition if isinstance(self.condition, Condition) else Condition(**self.condition)

    def _next_value(self, row):
        if self._cond_obj.is_true(row):
            return self.true_value.next_value(row) if hasattr(
                self.true_value, "next_value") else self.true_value
        else:
            return self.false_value.next_value(row) if hasattr(
                self.false_value, "next_value") else self.false_value


@attr.s(kw_only=True)
class Condition:
    """
    Dependent field condition which compares the results of a field expression with a value, using an operator function.

    In general it is easiest to use builtin Python "operator" functions such as `operator.or_`, `operator.and_`,
    `operator.eq` etc., however, it is possible to use a custom function if required (provided it accepts
    two values and returns a boolean value).
    """
    name = attr.ib(default=None)
    field = attr.ib()  # name of field to check or field definition (e.g. could nest IfElseField)
    operator = attr.ib()
    value = attr.ib()
    _operator_fn = attr.ib()

    @_operator_fn.default
    def _default_operator_fn(self):
        return create_package_class(self.operator)

    def is_true(self, row):
        return self._operator_fn(row.get(self.field), self.value)


@attr.s(kw_only=True)
class RepeatField(Field):
    """
    Field which repeats the generation of field values a random number of times within a specified range.

    The result is output as either a list or, if a glue string is provided, as a concatenated value separated by that
    string.
    """
    field: Field = attr.ib()
    min_repeats: int = attr.ib()
    max_repeats: int = attr.ib()
    glue: str = attr.ib(default=None)

    def _next_value(self, row):
        min_values = extract_number(self.min_repeats, row)
        max_values = extract_number(self.max_repeats, row)

        num_values = rnd.randrange(min_values, max_values)

        outputs = [self.field.next_value(row) for n in range(1, num_values + 1)]

        return self.glue.join(outputs) if self.glue else outputs


@attr.s(kw_only=True)
class NumberField(Field):
    """
    Field which generates a number based on a random float selection from a scipy statistical distribution.

    Available scipy distributions include all those from the scipy.stats module
    (see https://docs.scipy.org/doc/scipy/reference/stats.html).

    For custom distributions, any class can be used provided it follows the same constructor arguments (loc and scale)
    and has an rvs() function.

    Includes support for a mean and standard distribution. Also an optional decimal places (dp), min and max can be
    provided to produce numbers with these criteria.
    """
    distribution: str = attr.ib()
    mean: float = attr.ib()
    sd: float = attr.ib()
    min: float = attr.ib(default=None)
    max: float = attr.ib(default=None)
    dp: int = attr.ib(default=None)

    _dist_cls = attr.ib()

    @_dist_cls.default
    def _default_dist_cls(self):
        return create_package_class(self.distribution)(loc=self.mean, scale=self.sd)

    def _next_value(self, row):
        number = self._dist_cls.rvs()
        min = extract_number(self.min, row)
        max = extract_number(self.max, row)

        if (min and number < min) or (max and number > max):
            return self.next_value(row)

        if self.dp is not None:
            return round(number, self.dp)

        return number


@attr.s(kw_only=True)
class BooleanField(Field):
    """
    Field which generate a boolean (e.g. true/false) value based on a true_probability (default=0.5).

    The true_value (default=1) and false_value (default=0) which are returned can be specified.
    This field forms the basis of the derived GenderField
    """
    true_value: Any = attr.ib(default=1)
    false_value: Any = attr.ib(default=0)
    true_probability: float = attr.ib(default=0.5)

    def _next_value(self, row):
        return self.true_value if rnd.random() < self.true_probability else self.false_value


@attr.s(kw_only=True)
class DateField(NumberField):
    """
    Field which generates a date based on a random number of days from a scipy statistical distribution similarly to
    NumberField.

    The generated value is based on a mean date and standard deviation and the field 'adds' the generated number of
    days to the mean date.

    Available scipy distributions include all those from the scipy.stats module
    (see https://docs.scipy.org/doc/scipy/reference/stats.html).

    For custom distributions, any class can be used provided it follows the same constructor arguments (loc and scale)
    and has an rvs() function.

    Includes mean, min and max which can be provided as date objects or strings.
    If the latter, the mean_format, min_format and max_format define the date formats.
    """
    min_format: str = attr.ib(default=None)
    max_format: str = attr.ib(default=None)
    mean_format: str = attr.ib(default=None)
    format: str = attr.ib(default=None)
    use_years: bool = attr.ib(default=False)

    _dist_cls = attr.ib()

    @_dist_cls.default
    def _default_dist_cls(self):
        return create_package_class(self.distribution)(loc=0, scale=self.sd)

    def _next_value(self, row):
        min = extract_date(self.min, row, self.min_format)
        max = extract_date(self.max, row, self.max_format)
        mean = extract_date(self.mean, row, self.mean_format)

        num_to_mean = self._dist_cls.rvs()

        if self.use_years:
            num_to_mean *= 365.25

        date = mean + td(days=num_to_mean)

        if (min and date < min) or (max and date > max):
            return self.next_value(row)

        if self.format:
            return date.strftime(self.format)

        return date


def extract_number(value, row):
    """
    Extracts number to use for min/max or other input parameter.

    If value is a string, it will be assumed it is the name of a field in the row (and the value of that field will
    be returned).

    If it is a Field class, then the next_value function will be used to generate the value.

    Otherwise, the original value will be returned.

    :param value:
    :param row:
    :return:
    """
    if isinstance(value, str):
        if not value in row:
            raise ValueError(
                "Field with name '%s' is not present in the row or has not been generated yet" %
                value)
        return row.get(value)

    if isinstance(value, Field):
        return value.next_value(row)

    return value


def extract_date(value, row, date_format):
    """
    Extracts date to use for min/max or other input parameter.

    If value is a string, it will be assumed it is the name of a field in the row (and the value of that field will
    be converted into a date object.

    If it is a Field class, then the next_value function will be used to generate the value.

    Otherwise, the original value will be returned.

    :param value:
    :param row:
    :return:
    """
    if isinstance(value, str):
        if not value in row:
            raise ValueError(
                "Field with name '%s' is not present in the row or has not been generated yet" %
                value)

        data = row.get(value)
        if isinstance(data, datetime.date):
            return data

        return dt.strptime(data, date_format)

    if isinstance(value, Field):
        return value.next_value(row)

    return value
