from headfake import field
from unittest import mock
import datetime

from tests.field.test_field_common import MALE_VALUE, FEMALE_VALUE

row = {}


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

