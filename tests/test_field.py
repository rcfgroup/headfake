from headfake import field, Fieldset
import pytest
from unittest import mock
import datetime

MALE_NAME = "JEFF"
MALE_NAME2 = "BIFF"

FEMALE_NAME = "JENNIFER"
FEMALE_NAME2 = "JANE"

MALE_SURNAME = "BRIDGES"
FEMALE_SURNAME = "SAUNDERS"

MALE_VALUE = "M"
FEMALE_VALUE = "F"

ADDRESS_LINE_1 = "15 THE DRIVE"
ADDRESS_LINE_2 = "SOMEWHERETON"
ADDRESS_LINE_3 = "SOMEWHERESHIRE"
ADDRESS_POSTCODE = "SW1 3AB"
PHONE_NUMBER = "01234 567890"

row = {}


class mock_datetime:
    @classmethod
    def now(cls):
        return datetime.date(2020, 3, 24)


def test_IncrementIdFieldType_returns_incremental_values():
    id = field.IncrementIdGenerator(length=2)

    assert ["01","02","03","04","05","06","07"]==[id.select_id() for i in range(1,8)]

def test_IncrementIdFieldType_fails_if_passes_maximum():
    id = field.IncrementIdGenerator(length=2)

    [id.select_id() for i in range(1, 100)]

    with pytest.raises(ValueError,match = r"next number is greater than length"):
        id.select_id()

def test_IdFieldType_is_correct_length():
    id1 = field.IncrementIdGenerator(length=6)
    assert id1.select_id() == "000001"
    assert id1.select_id() == "000002"

    id1 = field.IncrementIdGenerator(length=4)
    assert id1.select_id() == "0001"
    assert id1.select_id() == "0002"

def test_RandomNoReuseIdFieldType_generates_random_no_with_no_replacement(monkeypatch):
    id = field.RandomNoReuseIdFieldType(length=3)

    monkeypatch.setattr("random.randrange",mock.Mock(side_effect=[5,8,4,6,5,9]))
    assert id.select_id() == "005"
    assert id.select_id() == "008"
    assert id.select_id() == "004"
    assert id.select_id() == "006"
    assert id.select_id() == "009"

def test_RandomNoReuseIdFieldType_generates_random_no_with_replacement(monkeypatch):
    id = field.RandomReuseIdFieldType(length=3)

    monkeypatch.setattr("random.randrange",mock.Mock(side_effect=[5,8,4,6,5,9]))
    assert id.select_id() == "005"
    assert id.select_id() == "008"
    assert id.select_id() == "004"
    assert id.select_id() == "006"
    assert id.select_id() == "005"
    assert id.select_id() == "009"

def test_IdField_returns_values_from_id_field_type_with_suffix_and_prefix():
    id_generator = mock.MagicMock(field.IncrementIdGenerator)
    id_generator.select_id.side_effect = ["003","006","005","008","004"]

    id = field.IdField(prefix="P", suffix="S", generator=id_generator)

    assert id.next_value(row) == "P003S"
    assert id.next_value(row) == "P006S"
    assert id.next_value(row) == "P005S"
    assert id.next_value(row) == "P008S"
    assert id.next_value(row) == "P004S"

def test_GenderField_returns_male_value_if_random_no_is_lt_male_probability(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.4999)
    gender = field.GenderField(male_value = MALE_VALUE, female_value = FEMALE_VALUE)
    obs = gender.next_value(row)
    assert obs == MALE_VALUE

def test_GenderField_returns_female_value_if_random_no_is_gt_or_eq_male_probability(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    gender = field.GenderField(male_value = MALE_VALUE, female_value = FEMALE_VALUE)
    obs = gender.next_value(row)
    assert obs == FEMALE_VALUE

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

def test_OptionValueField_chooses_value_basedon_probability_from_distribution(monkeypatch):
    n = mock.Mock()
    mock_choices = {"M":0.2,"F":0.8}
    n.return_value = "M"
    monkeypatch.setattr("random.choice",n)

    dob = field.OptionValueField(probabilities = mock_choices)

    assert dob.next_value(row) == "M"
    n.assert_called_with(dob._option_picks)

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

def test_ConcatField_joins_multiple_fields_together(monkeypatch):
    n = mock.Mock()
    n.side_effect = [123456787,123456787,123456783]
    monkeypatch.setattr("random.randrange",n)

    fields  = [field.ConstantField(value="X"),field.ConstantField(value="Y"),field.ConstantField(value="Z")]
    concat = field.ConcatField(fields = fields, glue=" ")

    assert concat.next_value(row) == "X Y Z"

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

def test_PhoneField_outputs_postcode(monkeypatch):
    f = mock.Mock()
    f.return_value.phone_number.return_value = PHONE_NUMBER

    monkeypatch.setattr("faker.Faker", f)

    assert field.PhoneField().next_value(row) == PHONE_NUMBER
