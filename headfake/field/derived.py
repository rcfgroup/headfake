from .core import Field, DerivedField, NumberField, BooleanField, extract_date
import attr
import datetime
import random as rnd
from typing import Dict, List, Any

from headfake.util import calculate_age


@attr.s(kw_only=True)
class DateOfBirthField(DerivedField):
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

    def _internal_field(self):
        return NumberField(mean=self.mean, sd=self.sd, min=self.min,
                           max=self.max, distribution=self.distribution)

    def _next_value(self, row):
        age_in_years = super()._next_value(row)

        age_in_days = age_in_years * 365.25
        dob = datetime.datetime.now() - datetime.timedelta(days=age_in_days)
        return dob.strftime(self.date_format)


@attr.s(kw_only=True)
class GenderField(DerivedField):
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

    def _internal_field(self):
        return BooleanField(true_value=self.male_value,
                            false_value=self.female_value, true_probability=self.male_probability)


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
    patient is deceased and when they died. The ages are specified in a dictionary of the form {"X1-Y1":R1, "X2-Y2":R2}.

    The risk is defined as the 1 in R risk of death.

    The end date to use to determine the age defaults to today, but can be set using the 'end_date' argument as a date
    object, a field name or a Field object.

    """
    deceased_true_value = attr.ib(default=1)
    deceased_false_value = attr.ib(default=0)
    dob_field: str = attr.ib()
    deceased_date_field: str = attr.ib(default=None)

    age_field: str = attr.ib(default=None)

    risk_of_death: Dict[str, str] = attr.ib()
    date_format = attr.ib()
    _risk_by_age: Dict[int, float] = attr.ib()

    end_date = attr.ib(default=datetime.date.today())
    end_date_format = attr.ib(default=None)
    generate_after = True

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
        self._dob_field = fieldset.field_map.get(self.dob_field)

        if self.deceased_date_field:
            fieldset.field_names.append(self.deceased_date_field)

        if self.age_field:
            fieldset.field_names.append(self.age_field)



    def _next_value(self, row):
        dob = row.get(self.dob_field)
        dob = datetime.datetime.strptime(dob, self._dob_field.date_format).date()

        today = extract_date(self.end_date, row, self.end_date_format)
        prev_date = dob
        curr_date = dob + datetime.timedelta(weeks=52)

        while (curr_date < today):
            curr_age = calculate_age(dob, curr_date)
            curr_risk = self._risk_by_age.get(curr_age)

            if curr_risk is not None and rnd.random() <= curr_risk:
                int_bt_curr_and_prev = curr_date - prev_date
                rnd_days_after_curr = rnd.randrange(0, int_bt_curr_and_prev.days)
                dod = curr_date + datetime.timedelta(days=rnd_days_after_curr)

                value = {self.name: self.deceased_true_value}

                if self.deceased_date_field:
                    value[self.deceased_date_field] = dod.strftime(self.date_format)

                if self.age_field:
                    value[self.age_field] = curr_age

                return value

            prev_date = curr_date
            curr_date = curr_date + datetime.timedelta(weeks=52)

        value = {self.name: self.deceased_false_value}
        if self.deceased_date_field:
            value[self.deceased_date_field] = ""

        if self.age_field:
            value[self.age_field] = curr_age

        return value



@attr.s(kw_only=True)
class AgeField(Field):
    """
    Calculates age in years from two fields or values. The specified from_value and to_value can be either strings,
    date objects or Fields. If the former, then it is treated as the name of the field to obtain from the row.
    """
    from_value = attr.ib()
    to_value = attr.ib()
    from_format = attr.ib(default=None)
    to_format = attr.ib(default=None)

    def _next_value(self, row: Dict[str, Any]):
        from_date = extract_date(self.from_value, row, self.from_format)
        to_date = extract_date(self.to_value, row, self.to_format)
        return calculate_age(from_date, to_date)
