import random as rnd
import faker
from faker.providers import person
from .util import create_package_class
import datetime as dt

class IncrementalField:
    def __init__(self, suffix, length, start_at):
        self.suffix = suffix
        self.length = length
        self.start_at = start_at
        self.current_no = self.start_at

    def next_value(self,row):
        curr_no  = str(self.current_no).zfill(self.length)
        self.current_no+=1
        return self.suffix + curr_no

class GenderField:
    def __init__(self, male_value, female_value, male_probability=0.5):
        self.male_value = male_value
        self.female_value = female_value
        self.male_probability = male_probability

    def next_value(self,row):
        return self.male_value if rnd.random() < self.male_probability else self.female_value

class NameField:
    def __init__(self, gender_field, uppercase=False, empty_probability=0):

        self.gender_field = gender_field
        self.uppercase = uppercase
        self.empty_probability = empty_probability
        self.fake = faker.Faker()
        self.fake.add_provider(person)

    @property
    def fieldset(self):
        return self._fieldset

    @fieldset.setter
    def fieldset(self, value):
        self.gender = value.fields.get(self.gender_field)
        self._fieldset = value

    def next_value(self, row):
        name = None
        if rnd.random() < self.empty_probability:
            return ""
        if self.gender.male_value:
            name = self._male_name()
        if self.gender.female_value:
            name = self._female_name()

        return name.upper() if self.uppercase else name

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
    def __init__(self, gender_field, uppercase=False, empty_probability=0, firstname_field=None):
        super().__init__(gender_field, uppercase, empty_probability)
        self.firstname_field = firstname_field

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

class DateOfBirthField():
    def __init__(self, min, max, mean, sd, distribution, date_format):
        self.min = min
        self.max = max
        self.mean = mean
        self.sd = sd
        self.distribution = create_package_class(distribution)(loc=self.mean, scale=self.sd)
        self.date_format = date_format

    def next_value(self, row):
        age_in_years = self.distribution.rvs()
        if age_in_years<self.min or age_in_years>self.max:
            return self.next_value(row)

        age_in_days = age_in_years * 365.25
        dob = dt.datetime.now() - dt.timedelta(days=age_in_days)
        return dob.strftime(self.date_format)

class OptionValueField():
    def __init__(self, probabilities):
        self.probabilities = probabilities
        self.option_picks = []

        for val, prob in probabilities.items():
            self.option_picks += [val] * int(prob*100)

    def next_value(self, row):
        return rnd.choice(self.option_picks)



