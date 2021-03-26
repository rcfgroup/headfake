from .core import Field, DerivedField, OptionValueField
import attr
import datetime
from headfake.util import create_package_class, calculate_age
import random as rnd
from typing import Dict, List


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
class GenderField(Field):
    """
    Field which generates gender values according to a 'male_probability' (default=0.5). Options include male_value (value of male selection), female_value (value of female
    selection and male_probability (probability that gender is male, default=0.5).

    e.g.
    ```python
    field = GenderField(male_value="M",female_value="F", male_probability=0.55)
    field.next_value(row)

    M
    F
    M
    M
    F
    ```
    """
    male_probability = attr.ib(default=0.5)
    male_value = attr.ib()
    female_value = attr.ib()


    def _next_value(self, row):
        return self.male_value if rnd.random() < self.male_probability else self.female_value

@attr.s(kw_only=True)
class NhsNoField(Field):
    """
    Mock NHS number field which creates valid NHS numbers with the correct checksum digit.
    See https://www.closer.ac.uk/wp-content/uploads/CLOSER-NHS-ID-Resource-Report-Apr2018.pdf for details.
    """
    _used_values: List[id] = attr.ib(factory=list)

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
            return self.next_value(row)

        return strval[0:3] + " " + strval[3:6] + " " + strval[6:9] + str(checkdigit)




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

