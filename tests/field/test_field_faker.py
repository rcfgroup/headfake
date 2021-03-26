from headfake import field, Fieldset
from unittest import mock
import datetime

from tests.field.test_field_common import MALE_VALUE, FEMALE_VALUE, MALE_NAME, FEMALE_NAME, MALE_SURNAME, \
    FEMALE_SURNAME, MALE_NAME2, FEMALE_NAME2, ADDRESS_LINE_1, ADDRESS_LINE_2, ADDRESS_LINE_3, ADDRESS_POSTCODE, \
    PHONE_NUMBER

row = {}

import random

class mock_datetime:
    @classmethod
    def now(cls):
        return datetime.date(2020, 3, 24)



def test_FirstNameField_returns_male_name_if_gender_field_is_male(monkeypatch):
    f = mock.Mock()
    f.return_value.first_name_male.return_value=MALE_NAME

    monkeypatch.setattr("faker.Faker", f)

    fn_field = field.FirstNameField(gender_field="gender")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"gender": gender})

    fn_field.init_from_fieldset(fset)

    obs = fn_field.next_value({"gender":MALE_VALUE})
    assert obs == MALE_NAME

def test_FirstNameField_returns_female_name_if_gender_field_is_female(monkeypatch):
    f = mock.Mock()
    f.return_value.first_name_female.return_value = FEMALE_NAME

    monkeypatch.setattr("faker.Faker", f)

    fn_field = field.FirstNameField(gender_field="gender")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"gender": gender})

    fn_field.init_from_fieldset(fset)

    obs = fn_field.next_value({"gender": FEMALE_VALUE})
    assert obs == FEMALE_NAME

def test_LastNameField_returns_male_last_name_if_gender_is_male(monkeypatch):
    f = mock.Mock()
    f.return_value.last_name_male.return_value = MALE_SURNAME

    monkeypatch.setattr("faker.Faker", f)

    ln_field = field.LastNameField(gender_field="gender")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"gender": gender})

    ln_field.init_from_fieldset(fset)

    obs = ln_field.next_value({"gender": MALE_VALUE})
    assert obs == MALE_SURNAME

def test_LastNameField_returns_female_last_name_if_gender_is_female(monkeypatch):
    f = mock.Mock()
    f.return_value.last_name_female.return_value = FEMALE_SURNAME

    monkeypatch.setattr("faker.Faker", f)

    ln_field = field.LastNameField(gender_field="gender")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"gender": gender})

    ln_field.init_from_fieldset(fset)

    obs = ln_field.next_value({"gender": FEMALE_VALUE})
    assert obs == FEMALE_SURNAME

def test_MiddleNameField_returns_different_name_if_same_as_first_name(monkeypatch):
    f = mock.Mock()
    f.return_value.first_name_female.side_effect = [FEMALE_NAME, FEMALE_NAME2]

    monkeypatch.setattr("faker.Faker", f)
    fn_field = field.FirstNameField(gender_field="gender")

    mn_field = field.MiddleNameField(gender_field="gender", first_name_field="first_name")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"first_name":fn_field,"gender": gender})

    mn_field.init_from_fieldset(fset)

    obs = mn_field.next_value({"gender": FEMALE_VALUE,"first_name":FEMALE_NAME})
    assert obs == FEMALE_NAME2

def test_MiddleNameField_returns_male_name_if_gender_is_male(monkeypatch):
    f = mock.Mock()
    f.return_value.first_name_male.return_value = MALE_NAME

    monkeypatch.setattr("faker.Faker", f)
    fn_field = field.FirstNameField(gender_field="gender")

    mn_field = field.MiddleNameField(gender_field="gender", first_name_field="first_name")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"first_name":fn_field,"gender": gender})

    mn_field.init_from_fieldset(fset)

    obs = mn_field.next_value({"gender": MALE_VALUE,"first_name":MALE_NAME2})
    assert obs == MALE_NAME

def test_MiddleNameField_returns_female_name_if_gender_is_female(monkeypatch):
    f = mock.Mock()
    f.return_value.first_name_female.return_value = FEMALE_NAME

    monkeypatch.setattr("faker.Faker", f)
    fn_field = field.FirstNameField(gender_field="gender")

    mn_field = field.MiddleNameField(gender_field="gender", first_name_field="first_name")

    gender = field.GenderField(male_value=MALE_VALUE, female_value=FEMALE_VALUE)

    fset = Fieldset(fields={"first_name":fn_field,"gender": gender})

    mn_field.init_from_fieldset(fset)

    obs = mn_field.next_value({"gender": FEMALE_VALUE,"first_name":FEMALE_NAME2})
    assert obs == FEMALE_NAME

def test_DateOfBirthField_creates_date_using_value_from_distribution(monkeypatch):
    n = mock.Mock()

    monkeypatch.setattr("scipy.stats.norm",n)

    monkeypatch.setattr("datetime.datetime", mock_datetime)

    n.return_value.rvs.return_value=25.3
    dob = field.DateOfBirthField(distribution = "scipy.stats.norm", min=0, max=105, mean=45, sd=13, date_format="%d/%m/%Y")
    assert dob.next_value(row) == "06/12/1994"

def test_AddressField_outputs_address(monkeypatch):
    f = mock.Mock()
    f.return_value.street_address.return_value = ADDRESS_LINE_1
    f.return_value.secondary_address.return_value = ADDRESS_LINE_2
    f.return_value.city.return_value = ADDRESS_LINE_3

    monkeypatch.setattr("faker.Faker", f)

    assert field.AddressField(line_no=1).next_value(row) == ADDRESS_LINE_1
    assert field.AddressField(line_no=2).next_value(row) == ADDRESS_LINE_2
    assert field.AddressField(line_no=3).next_value(row) == ADDRESS_LINE_3

def test_PostcodeField_outputs_postcode(monkeypatch):
    f = mock.Mock()
    f.return_value.postcode.return_value = ADDRESS_POSTCODE

    monkeypatch.setattr("faker.Faker", f)

    assert field.PostcodeField().next_value(row) == ADDRESS_POSTCODE

def test_PhoneField_outputs_phone_number(monkeypatch):
    f = mock.Mock()
    f.return_value.phone_number.return_value = PHONE_NUMBER

    monkeypatch.setattr("faker.Faker", f)

    assert field.PhoneField().next_value(row) == PHONE_NUMBER
