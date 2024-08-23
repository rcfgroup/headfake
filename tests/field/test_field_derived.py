from headfake import field
from unittest import mock
import datetime

from headfake.field import LookupField
from tests.field.test_field_common import MALE_VALUE, FEMALE_VALUE

row = {}
import numpy as np

class mock_datetime:
    @classmethod
    def now(cls):
        return datetime.date(2020, 3, 24)


def test_GenderField_returns_male_value_if_random_no_is_lt_male_probability(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.4999)
    gender = field.GenderField(male_value =MALE_VALUE, female_value =FEMALE_VALUE)
    obs = gender.next_value(row)
    assert obs == MALE_VALUE

def test_GenderField_returns_female_value_if_random_no_is_gt_or_eq_male_probability(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    gender = field.GenderField(male_value =MALE_VALUE, female_value =FEMALE_VALUE)
    obs = gender.next_value(row)
    assert obs == FEMALE_VALUE

def test_DateOfBirthField_creates_date_using_value_from_distribution(monkeypatch):
    n = mock.Mock()

    monkeypatch.setattr("scipy.stats.norm",n)

    monkeypatch.setattr("datetime.datetime", mock_datetime)

    n.return_value.rvs.return_value=25.3
    dob = field.DateOfBirthField(distribution = "scipy.stats.norm", min=0, max=105, mean=45, sd=13, date_format="%d/%m/%Y")
    assert dob.next_value(row) == "06/12/1994"

def test_NhsNoField_generates_valid_nhs_number(monkeypatch):
    n = mock.Mock()
    n.return_value = 123456787
    monkeypatch.setattr("random.randrange",n)

    nhs_no = field.NhsNoField()

    assert nhs_no.next_value(row) == "123 456 7873"
    n.assert_called_with(100000000, 999999999)

def test_NhsNoField_handles_invalid_nhs_number_by_reselecting(monkeypatch):
    n = mock.Mock()
    n.side_effect = [123456789, 123456787]
    monkeypatch.setattr("random.randrange",n)

    nhs_no = field.NhsNoField()

    assert nhs_no.next_value(row) == "123 456 7873"

def test_NhsNoField_handles_duplicate_nhs_number_by_reselecting(monkeypatch):
    n = mock.Mock()
    n.side_effect = [123456787,123456787,123456783]
    monkeypatch.setattr("random.randrange",n)

    nhs_no = field.NhsNoField()

    assert nhs_no.next_value(row) == "123 456 7873"
    assert nhs_no.next_value(row) == "123 456 7830"

def test_AgeField_calculates_correct_age_using_to_and_from_fields_containing_dates():
    age = field.AgeField(from_value=LookupField(field="from_date"),to_value=LookupField(field="to_date"))
    assert age.next_value({"from_date":datetime.date(1953,3,5),"to_date":datetime.date(2010,5,4)}) == 57

def test_AgeField_calculates_correct_age_using_to_and_from_fields_containing_strings():
    age = field.AgeField(from_value=LookupField(field="from_date"),to_value=LookupField(field="to_date"), from_format="%d/%m/%Y",to_format="%d/%m/%Y")
    assert age.next_value({"from_date":"05/03/1953","to_date":"04/05/2010"}) == 57

def test_AgeField_calculates_correct_age_using_to_and_from_values_as_fields():
    from headfake import HeadFake
    HeadFake.set_seed(123)
    age = field.AgeField(
        from_value=field.DateField(
            min=datetime.date(1953,3,5),
            mean=datetime.date(1974,1,1),
            sd=13,
            max=datetime.date.today(),
            use_years=True,
            distribution="scipy.stats.norm"
        ),
        to_value=datetime.date.today()
    )
    assert age.next_value({}) == 64
    assert age.next_value({}) == 37
    assert age.next_value({}) == 46

def test_DeceasedField_simulates_death_based_on_risks_and_returns_additional_fields():
    from headfake.fieldset import Fieldset
    from headfake import HeadFake

    dob = field.DateOfBirthField(distribution = "scipy.stats.norm", min=0, max=105, mean=45, sd=13, date_format="%d/%m/%Y")
    deceased = field.DeceasedField(
        deceased_true_value=1,
        deceased_false_value=0,
        dob_field="dob",
        deceased_date_field="dod",
        age_field="age",
        risk_of_death={"30-100":"2"},
        date_format = "%Y-%m-%d",
    )
    fieldset = Fieldset(fields={"dob":dob, "deceased":deceased})

    HeadFake.set_seed(543)
    deceased.init_from_fieldset(fieldset)
    deceased.next_value({"dob":"03/04/1983"}) == {'age': 33, 'deceased': 1, 'dod': '2018-02-04'}