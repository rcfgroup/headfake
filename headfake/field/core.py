"""
Fake/mock field generation logic
"""

import csv
import random as rnd
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime as dt, timedelta as td
import datetime

import attr
import faker

from headfake.error import TransformerError
from headfake.transformer import Transformer
from headfake.util import create_package_class, locate_file, handle_missing_keyword, new_field_name

import numpy as np
from functools import partial

@attr.s(kw_only=True)
class Field(ABC):
    """Acts as abstract Field class.

    Fields use the attrs module to handle available/required class attributes/defaults.

    Args:
        transformers (list): Optional list of transformer objects which act upon on field values at various points.
        name (str): Optional name of field (defaults to incremental number)

    """
    transformers: List[Transformer] = attr.ib(factory=list)
    final_transformers: List[Transformer] = attr.ib(factory=list)
    name: Optional[str] = attr.ib(default=new_field_name())
    generate_after:bool = False # static property to force the value to be generated after other field values have been generated
    hidden:bool = attr.ib(default=False) # field which is hidden from the final output
    error_value:Any = attr.ib(default=None)
    params = attr.ib(factory=dict)

    _transform = attr.ib()

    @_transform.default
    def _default_transform(self):
        if self.transformers:
            return partial(transform_value, field=self, transformers=self.transformers)
        else:
            return lambda row, value: value

    def after_init_params(self):
        [t.init_params(self) for t in self.transformers]

    def init_params(self):
        pass

    def init_transformers(self, fieldset):
        for transformer in self.transformers + self.final_transformers:
            transformer.init_from_fieldset(fieldset)

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

    def next_value(self, row: Dict[str, Any], **kwargs) -> Union[Any, Dict[str, Any]]:
        """Gets next generated value for field.

        Acts as a decorator around the private '_next_value' method.
        If 'transformers' have been provided in the constructor they will act on the value after it has been
        generated.

        Args:
            row: The current data row as a dictionary

        Returns:
            Dictionary containing multiple fields OR a single field value

        """

        try:
            val = self._next_value(row)

            val = self._transform(row=row, value=val)
        except Exception as ex:
            if self.error_value:
                return self.error_value

            raise ex

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

def transform_value(field, row, value, transformers):
        for t in transformers:
            try:
                value = t.transform(field, row, value)
            except Exception as ex:
                raise TransformerError(field, t, row, ex)

        return value


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
    """Field which generates constant values. Automatically replaces scalar values (e.g. string, number) when fieldsets
    are created.
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
        return create_package_class(self.distribution)(loc=self.mean, scale=self.sd, **self.params)

    def _next_value(self, row):
        number = self._dist_cls.rvs()
        min = extract_number(self.min, row)
        max = extract_number(self.max, row)

        if (min and number < min) or (max and number > max):
            return self._next_value(row)

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

    If a 'format' parameter is provided, the date is output as a string, if not it is output as a date object.

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

@attr.s(kw_only=True)
class OperationField(Field):
    """
    Field which generates a value using an operation to process two values (e.g. add, subtract).
    Like the 'Condition' used in IfElseField, it is easiest to use builtin Python "operator" functions such as
    `operator.add`, `operator.sub` but a custom function can be used if needed.

    The first and second values can be field definitions or scalar values (e.g. strings, numbers, dates).

    """
    operator = attr.ib()
    first_value = attr.ib()
    second_value = attr.ib()
    _operator_fn = attr.ib()

    @_operator_fn.default
    def _default_operator_fn(self):
        return create_package_class(self.operator)

    def _determine_value(self, row, property):
        return property.next_value(row) if hasattr(
            property, "next_value") else property

    def _next_value(self, row):
        first_value = self._determine_value(row, self.first_value)
        second_value = self._determine_value(row, self.second_value)

        return self._operator_fn(first_value, second_value)

@attr.s(kw_only=True)
class LookupField(Field):
    """
    Field which returns the value of another specified field.
    """

    field = attr.ib()

    def _next_value(self, row):
        return row.get(self.field)



def extract_number(value, row):
    """
    Extracts number to use for min/max or other input parameter.

    If value is numeric (int or float) then it will be simply returned.

    If it is a Field class, then the next_value function will be used to generate the value.

    Otherwise an attempt will be made to convert it to a number.

    :param value:
    :param row:
    :return:
    """

    if value is None:
        return None

    if isinstance(value, Field):
        value = value.next_value(row)

    if isinstance(value, float) or isinstance(value, int):
        return value

    return float(value)


def extract_date(value, row, date_format):
    """
    Extracts date to use for min/max or other input parameter.

    If value is a datetime then it will be simply returned.

    If it is a Field class, then the next_value function will be used to generate the value.

    Otherwise an attempt will be made to extract the date from it.


    :param value:
    :param row:
    :return:
    """

    if value is None:
        return None

    if isinstance(value, Field):
        value = value.next_value(row)

    if isinstance(value, datetime.date):
        return value

    return dt.strptime(value, date_format)


