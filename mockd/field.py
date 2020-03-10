import random as rnd
import faker
from faker.providers import person

from mockd.error import ChangeValue
from .util import create_package_class, calculate_age
import datetime as dt
import csv

LOCALE = "en_GB"

class Field:
    default_params = {}
    def __init__(self, **kwargs):
        def_params = self.default_params
        def_params["transformers"]=[]
        for k,v in self.default_params.items():
            if k not in kwargs:
                kwargs[k]=v

        for k,v in kwargs.items():
            setattr(self, k, v)

        self.init_params()
        [t.init_params(self) for t in self.transformers]

    @property
    def names(self):
        return [self.name]

    def init_params(self):
        pass

    def init_from_fieldset(self, fieldset):
        pass

    def next_value(self, row):
        try:
            [t.before_next(self, row) for t in self.transformers]
        except ChangeValue as ex:
            return ex.value

        val = self._next_value(row)

        for t in self.transformers:
            val = t.after_next(self, row, val)

        return val

class IdField(Field):
    default_params = {
        "prefix":"",
        "start_at":0,
        "reuse_ids":False,
        "suffix":""
    }
    def init_params(self):
        self.current_no = self.start_at

        if self.type == "incremental":
            self._id_func = self._increment
        elif self.type == "random_reuse":
            self._id_func = self._random_reuse
            self.end_at = int("9" * self.length)
        else:
            self._id_func = self._random_no_reuse
            self.end_at = int("9" * self.length)
            self.used_values = []

    def _next_value(self,row):
        return self._id_func(row)

    def _increment(self, row):
        curr_no  = str(self.current_no).zfill(self.length)
        self.current_no+=1
        return self.prefix + curr_no + self.suffix

    def _random_no_reuse(self, row):
        val = rnd.randrange(self.start_at, self.end_at)
        if val in self.used_values:
            return self._random(row)

        if self.reuse_ids is False:
            self.used_values.append(val)

        curr_no  = str(val).zfill(self.length)

        return self.prefix + curr_no + self.suffix

    def _random_reuse(self, row):
        val = rnd.randrange(self.start_at, self.end_at)
        curr_no  = str(val).zfill(self.length)

        return self.prefix + curr_no + self.suffix

class GenderField(Field):
    default_params = {"male_probability":0.5}

    def _next_value(self,row):
        return self.male_value if rnd.random() < self.male_probability else self.female_value

class NameField(Field):
    def init_params(self):
        self.fake = faker.Faker(LOCALE)
        self.fake.add_provider(person)

    def init_from_fieldset(self, fieldset):
        self.gender = fieldset.fields.get(self.gender_field)

    def _next_value(self, row):
        name = None
        if self.gender.male_value:
            name = self._male_name()
        if self.gender.female_value:
            name = self._female_name()

        return name


class FirstNameField(NameField):
    def _male_name(self):
        return self.fake.first_name_male()

    def _female_name(self):
        return self.fake.first_name_female()

class LastNameField(NameField):
    def _male_name(self):
        return self.fake.last_name_male()

    def _female_name(self):
        return self.fake.last_name_female()

class MiddleNameField(NameField):
    def _male_name(self):
        return self.fake.last_name_male()

    def _female_name(self):
        return self.fake.last_name_female()

    def next_value(self, row):
        val = super().next_value(row)
        if val == "":
            return val
        if val == row.get(self.firstname_field):
            return self.next_value(row)

        return val

class DateOfBirthField(Field):
    def init_params(self):
        self.dist_cls = create_package_class(self.distribution)(loc=self.mean, scale=self.sd)

    def _next_value(self, row):
        age_in_years = self.dist_cls.rvs()
        if age_in_years<self.min or age_in_years>self.max:
            return self.next_value(row)

        age_in_days = age_in_years * 365.25
        dob = dt.datetime.now() - dt.timedelta(days=age_in_days)
        return dob.strftime(self.date_format)

class OptionValueField(Field):
    def init_params(self):
        self.option_picks = []

        for val, prob in self.probabilities.items():
            self.option_picks += [val] * int(prob*100)

    def next_value(self, row):
        return rnd.choice(self.option_picks)

class NhsNoField(Field):
    def init_params(self):
        self.used_values = []

    def _next_value(self, row):
        val = rnd.randrange(100000000, 999999999)
        if val in self.used_values:
            return self.next_value(row)

        self.used_values.append(val)

        strval = str(val)
        checksum = 0

        multiplier = 10

        for char in strval:
            checksum+=(multiplier * int(char))
            multiplier-=1

        checkdigit = 11 - (checksum % 11)
        if checkdigit == 11:
            checkdigit = 0

        if checkdigit == 10:
            return self.next_value(row)

        return strval[0:3] + " " + strval[3:6] + " " + strval[6:9] + str(checkdigit)

class ConstantField(Field):
    def next_value(self, row):
        return self.value

class AddressField(Field):
    def init_params(self):
        self.fake = faker.Faker(LOCALE)

    def _next_value(self, row):
        if self.line_no == 1:
            return self.fake.street_address()

        if self.line_no == 2:
            return self.fake.secondary_address()

        if self.line_no == 3:
            return self.fake.city()

        if self.line_no == 4:
            return ""

class PostcodeField(Field):
    def init_params(self):
        self.fake = faker.Faker(LOCALE)

    def next_value(self, row):
        return self.fake.postcode()

class PhoneField(Field):
    def init_params(self):
        self.fake = faker.Faker(LOCALE)

    def _next_value(self, row):
        return self.fake.phone_number()

class ConcatField(Field):
    def _next_value(self, row):
        val = ""
        for field in self.fields:
            val+=field.next_value(row)

        return val

class DeceasedField(Field):
    def init_params(self):
        self.dob_field_name = self.dob_field

    def init_from_fieldset(self, fieldset):
        self.dob_field = fieldset.fields.get(self.dob_field)

        self.risk_by_age = {}
        for k,v in self.risk_of_death.items():
            from_age, to_age = k.split("-")

            risk = 1/int(v)
            for i in range(int(from_age), int(to_age)+1):
                self.risk_by_age[i] = risk

    def _next_value(self, row):
        dob = row.get(self.dob_field_name)
        dob = dt.datetime.strptime(dob, self.dob_field.date_format).date()

        today = dt.date.today()
        prev_date = dob
        curr_date = dob + dt.timedelta(weeks=52)

        while(curr_date<today):
            curr_age = calculate_age(dob, curr_date)
            curr_risk = self.risk_by_age[curr_age]

            if rnd.random() <= curr_risk:
                int_bt_curr_and_prev = curr_date - prev_date
                rnd_days_after_curr = rnd.randrange(0,int_bt_curr_and_prev.days)
                dod = curr_date + dt.timedelta(days=rnd_days_after_curr)

                return {self.name:1, self.deceased_date_field:dod.strftime(self.date_format)}

            prev_date = curr_date
            curr_date = curr_date + dt.timedelta(weeks=52)

        return {self.name: 0, self.deceased_date_field: ""}

    def _age(self, start_date, end_date):
        pass

    @property
    def names(self):
        return [self.name,self.deceased_date_field]

class MapFileField(Field):
    def init_params(self):
        input_file = self.mapping_file
        with open(input_file, "r") as out:
            reader = csv.DictReader(out)
            self.map = {l.get(self.key_field):l for l in reader}

    def _next_value(self, row):
        rnd_key = rnd.choice(list(self.map.keys()))
        return rnd_key

class LookupMapFileField(Field):
    def _next_value(self, row):
        map_field = self.fieldset.fields.get(self.map_field)
        map_line = map_field.map.get()
        return map_field.
