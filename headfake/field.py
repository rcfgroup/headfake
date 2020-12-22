# Fake/mock field generation logic

import csv
import datetime
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
class GenderField(Field):
    """
    Field which generates gender values according to a 'male_probability' (default=0.5). Options include male_value (value of male selection), female_value (value of female
    selection and male_probability (probability that gender is male, default=0.5).

    e.g.
    ....
    field = GenderField(male_value="M",female_value="F", male_probability=0.55)
    field.next_value(row)

    M
    F
    M
    M
    F

    """

    male_probability = attr.ib(default=0.5)
    male_value = attr.ib()
    female_value = attr.ib()

    def _next_value(self, row):
        return self.male_value if rnd.random() < self.male_probability else self.female_value


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
class NameField(FakerField):
    """
    Base for a name field which uses faker to generate. The supplied 'gender_field' points to the field in the fieldset
    which generates the gender value. It uses this field and row value to determine whether the generated name is male
    or female.
    """
    gender_field = attr.ib()

    def init_from_fieldset(self, fieldset):
        self.gender = fieldset.fields.get(self.gender_field)

    def _next_value(self, row):
        if row.get(self.gender_field) == self.gender.male_value:
            return self._male_name()
        if row.get(self.gender_field) == self.gender.female_value:
            return self._female_name()

class FirstNameField(NameField):
    """
    Generate first name based on gender using the faker module (see NameField).
    """
    def _male_name(self):
        return self._fake.first_name_male()

    def _female_name(self):
        return self._fake.first_name_female()


class LastNameField(NameField):
    """
    Generate last name using the faker module.
    """
    def _male_name(self):
        return self._fake.last_name_male()

    def _female_name(self):
        return self._fake.last_name_female()


@attr.s(kw_only=True)
class MiddleNameField(NameField):
    """
    Mock middle name field.
    """

    first_name_field = attr.ib()

    def _male_name(self):
        return self._fake.first_name_male()

    def _female_name(self):
        return self._fake.first_name_female()

    def next_value(self, row):
        val = super().next_value(row)
        if val == "":
            return val
        if val == row.get(self.first_name_field):
            return self.next_value(row)

        return val


@attr.s(kw_only=True)
class DateOfBirthField(Field):
    """
    Mock date of birth field. Calculates age based on random float selection from a scipy statistical distribution.
    This is multiplied by 365.25 to get age in days and a delta age (in days) from now is determined.
    The date is then output according to the date_format property.

    A min and max property are also required to keep the distribution within a particular range.
    """
    distribution: str = attr.ib()
    mean: float = attr.ib()
    sd: float = attr.ib()
    min: float = attr.ib()
    max: float = attr.ib()
    date_format: str = attr.ib()

    _dist_cls = attr.ib()

    @_dist_cls.default
    def _default_dist_cls(self):
        return create_package_class(self.distribution)(loc=self.mean, scale=self.sd)

    def _next_value(self, row):
        age_in_years = self._dist_cls.rvs()
        if age_in_years < self.min or age_in_years > self.max:
            return self.next_value(row)

        age_in_days = age_in_years * 365.25
        dob = datetime.datetime.now() - datetime.timedelta(days=age_in_days)
        return dob.strftime(self.date_format)


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


@attr.s
class NhsNoField(Field):
    """
    Mock NHS number field which creates valid NHS numbers with the correct checksum digit.
    See https://www.closer.ac.uk/wp-content/uploads/CLOSER-NHS-ID-Resource-Report-Apr2018.pdf for details.
    """
    _used_values = attr.ib(factory=list)

    def _next_value(self, row):
        val = rnd.randrange(100000000, 999999999)
        if val in self._used_values:
            return self._next_value(row)

        self._used_values.append(val)

        strval = str(val)
        checksum = 0

        multiplier = 10

        for char in strval:
            checksum += (multiplier * int(char))
            multiplier -= 1

        checkdigit = 11 - (checksum % 11)
        if checkdigit == 11:
            checkdigit = 0

        if checkdigit == 10:
            return self._next_value(row)

        return strval[0:3] + " " + strval[3:6] + " " + strval[6:9] + str(checkdigit)


@attr.s(kw_only=True)
class ConstantField(Field):
    """
    Mock constant field.
    """
    value = attr.ib()

    def _next_value(self, row):
        return self.value


@attr.s
class AddressField(FakerField):
    """
    Mock address line field.
    """

    line_no = attr.ib()

    def _next_value(self, row):
        if self.line_no == 1:
            return self._fake.street_address()

        if self.line_no == 2:
            return self._fake.secondary_address()

        if self.line_no == 3:
            return self._fake.city()

        if self.line_no == 4:
            return ""


@attr.s(kw_only=True)
class PostcodeField(FakerField):
    """
    Mock postcode field.
    """

    def _next_value(self, row):
        return self._fake.postcode()


@attr.s(kw_only=True)
class PhoneField(FakerField):
    """
    Mock phone number field.
    """

    def _next_value(self, row):
        return self._fake.phone_number()


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
class DeceasedField(Field):
    """
    Deceased mock field which uses a list of age range/mortality risk and a simulated patient 'aging' to determine if a
    patient is deceased and when they died.
    """
    deceased_true_value = attr.ib(default=1)
    deceased_false_value = attr.ib(default=0)
    dob_field: str = attr.ib()
    deceased_date_field: str = attr.ib()

    risk_of_death: Dict[str, str] = attr.ib()
    date_format = attr.ib()
    _risk_by_age: Dict[int, float] = attr.ib()

    @_risk_by_age.default
    def _default_risk_by_age(self):
        risk_by_age = {}
        for k, v in self.risk_of_death.items():
            from_age, to_age = k.split("-")

            risk = 1 / int(v)
            for i in range(int(from_age), int(to_age) + 1):
                risk_by_age[i] = risk

        return risk_by_age

    def init_from_fieldset(self, fieldset):
        self._dob_field = fieldset.fields.get(self.dob_field)

    def _next_value(self, row):
        dob = row.get(self.dob_field)
        dob = datetime.datetime.strptime(dob, self._dob_field.date_format).date()

        today = datetime.date.today()
        prev_date = dob
        curr_date = dob + datetime.timedelta(weeks=52)

        while (curr_date < today):
            curr_age = calculate_age(dob, curr_date)
            curr_risk = self._risk_by_age[curr_age]

            if rnd.random() <= curr_risk:
                int_bt_curr_and_prev = curr_date - prev_date
                rnd_days_after_curr = rnd.randrange(0, int_bt_curr_and_prev.days)
                dod = curr_date + datetime.timedelta(days=rnd_days_after_curr)

                return {self.name: self.deceased_true_value, self.deceased_date_field: dod.strftime(self.date_format)}

            prev_date = curr_date
            curr_date = curr_date + datetime.timedelta(weeks=52)

        return {self.name: self.deceased_false_value, self.deceased_date_field: ""}

    def _age(self, start_date, end_date):
        pass

    @property
    def names(self):
        return [self.name, self.deceased_date_field]


@attr.s(kw_only=True)
class MapFileField(Field):
    """
    Acts as focal point for random selection from a 'mapping_file'. N.B. Currently the mapping file is an absolute path
    to a file, but in future it should take into account interlinked fieldsets.

    The 'key_field' has two roles:

    1) it specifies the field in the mapping file where the values in this field come from
    2) it is used as the key to lookup values when used in conjunction with one or LookupMapFileFields

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
class TimeField(FakerField):
    """
    Create mock time using faker
    """
    format = attr.ib("%H:%M")

    def _next_value(self, row):
        return self._fake.time(pattern=self.format)
