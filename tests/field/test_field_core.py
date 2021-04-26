import logging

from headfake import field, Fieldset
import pytest
from unittest import mock
import datetime

row = {}

import random

class mock_datetime:
    @classmethod
    def now(cls):
        return datetime.date(2020, 3, 24)


def test_IncrementIdGenerator_returns_incremental_values():
    id = field.IncrementIdGenerator(length=2)

    assert ["01","02","03","04","05","06","07"]==[id.select_id() for i in range(1,8)]

def test_IncrementIdGenerator_fails_if_passes_maximum():
    id = field.IncrementIdGenerator(length=2)

    [id.select_id() for i in range(1, 100)]

    with pytest.raises(ValueError,match = r"next number is greater than length"):
        id.select_id()

def test_IdGenerator_is_correct_length():
    id1 = field.IncrementIdGenerator(length=6)
    assert id1.select_id() == "000001"
    assert id1.select_id() == "000002"

    id1 = field.IncrementIdGenerator(length=4)
    assert id1.select_id() == "0001"
    assert id1.select_id() == "0002"

def test_RandomNoReuseIdGenerator_generates_random_no_with_no_replacement(monkeypatch):
    id = field.RandomNoReuseIdGenerator(length=3)

    monkeypatch.setattr("random.randrange",mock.Mock(side_effect=[5,8,4,6,5,9]))
    assert id.select_id() == "005"
    assert id.select_id() == "008"
    assert id.select_id() == "004"
    assert id.select_id() == "006"
    assert id.select_id() == "009"

def test_RandomNoReuseIdGenerator_generates_random_no_with_replacement(monkeypatch):
    id = field.RandomReuseIdGenerator(length=3)

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


def test_OptionValueField_chooses_value_basedon_probability_from_distribution(monkeypatch):
    n = mock.Mock()
    mock_choices = {"M":0.2,"F":0.8}
    n.return_value = "M"
    monkeypatch.setattr("random.choice",n)

    dob = field.OptionValueField(probabilities = mock_choices)

    assert dob.next_value(row) == "M"
    n.assert_called_with(dob._option_picks)


def test_ConcatField_joins_multiple_fields_together(monkeypatch):
    n = mock.Mock()
    n.side_effect = [123456787,123456787,123456783]
    monkeypatch.setattr("random.randrange",n)

    fields  = [field.ConstantField(value="X"),field.ConstantField(value="Y"),field.ConstantField(value="Z")]
    concat = field.ConcatField(fields = fields, glue=" ")

    assert concat.next_value(row) == "X Y Z"


import operator

def test_IfElseField_handles_simple_setup():
    fset = Fieldset(fields={"gender": ""})

    gender_cond = field.Condition(
        field = "gender",
        operator = operator.eq,
        value= "M"
    )

    if_else = field.IfElseField(
        condition = gender_cond,
        true_value = "MR",
        false_value = "MRS"
    )

    if_else.init_from_fieldset(fset)

    assert if_else.next_value({"gender":"M"}) == "MR"

    assert if_else.next_value({"gender": "F"}) == "MRS"

def test_IfElseField_handles_nested_setup():
    fset = Fieldset(fields={"marital_status": "M"})

    gender_cond = field.Condition(
        field="gender",
        operator=operator.eq,
        value="M"
    )

    ms_test_cond = field.Condition(
        field = "marital_status",
        operator = operator.eq,
        value= "M"
    )

    ms_if_else = field.IfElseField(
        condition=ms_test_cond,
        true_value="MRS",
        false_value="MISS"
    )

    gender_if_else = field.IfElseField(
        condition = gender_cond,
        true_value = "MR",
        false_value = ms_if_else
    )

    gender_if_else.init_from_fieldset(fset)

    assert gender_if_else.next_value({"gender":"M","marital_status":"M"}) == "MR"
    assert gender_if_else.next_value({"gender": "M", "marital_status": "S"}) == "MR"

    assert gender_if_else.next_value({"gender":"F","marital_status": "S"}) == "MISS"
    assert gender_if_else.next_value({"gender": "F", "marital_status": "M"}) == "MRS"

def test_IfElseField_handles_non_if_else_logic():
    fset = Fieldset(fields={"marital_status": "M"})
    random.seed(5)
    gender_cond = field.Condition(
        field="gender",
        operator=operator.eq,
        value="M"
    )


    ms_test_cond = field.Condition(
        field = "marital_status",
        operator = operator.eq,
        value= "M"
    )


    female_ov = field.OptionValueField(
        probabilities = {
            "MISS": 0.7,
            "MS": 0.1,
            "DR": 0.1,
            "PROF": 0.1
        })

    ms_if_else = field.IfElseField(
        condition=ms_test_cond,
        true_value="MRS",
        false_value=female_ov
    )


    gender_if_else = field.IfElseField(
        condition = gender_cond,
        true_value = "MR",
        false_value = ms_if_else
    )

    gender_if_else.init_from_fieldset(fset)

    assert gender_if_else.next_value({"gender":"M","marital_status":"M"}) == "MR"
    assert gender_if_else.next_value({"gender": "M", "marital_status": "S"}) == "MR"
    assert gender_if_else.next_value({"gender":"F","marital_status": "S"}) == "MS"
    assert gender_if_else.next_value({"gender": "F", "marital_status": "S"}) == "MISS"
    assert gender_if_else.next_value({"gender": "F", "marital_status": "S"}) == "PROF"


def test_RepeatField_generates_list_of_values():
    random.seed(124)
    gender_field = field.RepeatField(
        field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
        min_repeats=3,
        max_repeats=7
    )

    assert gender_field.next_value({}) == ['M', 'M', 'F', 'M', 'F']
    assert gender_field.next_value({}) == ['M', 'M', 'M']

def test_RepeatField_generates_joined_list_of_values():
    random.seed(124)
    gender_field = field.RepeatField(
        field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
        min_repeats=3,
        max_repeats=7,
        glue=","
    )

    assert gender_field.next_value({}) == "M,M,F,M,F"
    assert gender_field.next_value({}) == "M,M,M"

def test_RepeatField_nested_generates_multiple_joined_list_of_values():
    random.seed(124)
    gender_field = field.RepeatField(
        field = field.RepeatField(
            field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
            min_repeats=3,
            max_repeats=7,
            glue=","
        ),
        min_repeats=2,
        max_repeats=8,
        glue="|"
    )

    assert gender_field.next_value({}) == "M,F,M|M,M,F,F,M|F,M,M,M,M,M|M,F,M,M,F"
    assert gender_field.next_value({}) == "M,M,F|F,M,M|F,F,M,M,F,M|F,M,M,M,M,M|F,M,M|F,M,M"

MOCK_NORM_NUM1 = 3.131313

def test_NumberField_generates_random_number_with_no_formatting(monkeypatch):
    monkeypatch.setattr("scipy.stats.norm",mock_norm)
    number_field = field.NumberField(
        distribution = "scipy.stats.norm",
        mean=2,
        sd=0.5
    )
    assert number_field.next_value({}) == MOCK_NORM_NUM1

class mock_norm:
    def __init__(self, **kwargs):
        pass

    def rvs(self):
        return MOCK_NORM_NUM1

def test_NumberField_generates_random_number_with_specified_decimal_places(monkeypatch):
    monkeypatch.setattr("scipy.stats.norm",mock_norm)
    random.seed(125)
    number_field = field.NumberField(
        distribution = "scipy.stats.norm",
        mean=2,
        sd=0.5,
        dp=2
    )
    assert number_field.next_value({}) == 3.13


def test_BooleanField_returns_default_values_if_no_parameters(monkeypatch):
    random.seed(120)
    gender = field.BooleanField()

    assert gender.next_value(row) == 0
    assert gender.next_value(row) == 1



def test_BooleanField_uses_value_parameters_if_provided(monkeypatch):

    random.seed(120)
    gender = field.BooleanField(true_value=True,false_value=False)

    assert gender.next_value(row) is False
    assert gender.next_value(row) is True


def test_BooleanField_returns_value_based_on_true_probability_parameter(monkeypatch):

    gender = field.BooleanField(true_probability=0.3)

    monkeypatch.setattr("random.random", lambda: 0.29)

    assert gender.next_value(row) == 1

    monkeypatch.setattr("random.random", lambda: 0.31)

    assert gender.next_value(row) == 0


def test_NumberField_returns_value_within_range_of_two_value(monkeypatch):

    fset = Fieldset(fields=[
        field.NumberField(
            name="num",
            distribution="scipy.stats.norm",
            sd=3,
            mean=0,
            min=-2,
            max=2,
            dp=1
        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['num']>-2 and item['num']<2

def test_NumberField_returns_value_within_range_of_two_existing_fields(monkeypatch):

    fset = Fieldset(fields=[
        field.NumberField(
            name="floor",
            distribution="scipy.stats.norm",
            sd=1,
            mean=-5,
            min=-3,
            dp=0
        ),
        field.NumberField(
            name="ceil",
            distribution="scipy.stats.norm",
            sd=1,
            mean=5,
            max=3,
            dp=0
        ),
        field.NumberField(
            name="num",
            distribution="scipy.stats.norm",
            sd=3,
            mean=0,
            min="floor",
            max="ceil",
            dp=1
        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['num']>item['floor'] and item['num']<item['ceil']

def test_NumberField_returns_value_within_range_of_two_embedded_fields(monkeypatch):

    fset = Fieldset(fields=[
        field.NumberField(
            name="num",
            distribution="scipy.stats.norm",
            sd=3,
            mean=0,
            min=field.NumberField(
                name="floor",
                distribution="scipy.stats.norm",
                sd=1,
                mean=-5,
                min=-3,
                dp=0
            ),
            max=field.NumberField(
                name="ceil",
                distribution="scipy.stats.norm",
                sd=1,
                mean=5,
                max=3,
                dp=0
            ),
            dp=1
        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['num']>-3 and item['num']<3

def test_DateField_returns_value_within_range_of_two_values_with_specified_sd_in_days(monkeypatch):
    min = datetime.date(2020,1,1)
    max = datetime.date(2020,6,1)

    fset = Fieldset(fields=[
        field.DateField(
            name="date",
            distribution="scipy.stats.norm",
            sd=10,
            mean=datetime.date(2020,3,1),
            min=min,
            max=max,

        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['date']>min and item['date']<max

def test_DateField_returns_value_within_range_of_two_values_with_specified_sd_in_years(monkeypatch):
    min = datetime.date(1954,1,1)
    max = datetime.date(2020,6,1)

    fset = Fieldset(fields=[
        field.DateField(
            name="date",
            distribution="scipy.stats.norm",
            sd=5,
            mean=datetime.date(1970,3,1),
            min=min,
            max=max,
            use_years=True
        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['date']>min and item['date']<max


def test_DateField_returns_value_within_range_of_two_values_with_specified_sd_in_years(monkeypatch):
    min = datetime.date(1954,1,1)
    max = datetime.date(2020,6,1)

    fset = Fieldset(fields=[
        field.DateField(
            name="date",
            distribution="scipy.stats.norm",
            sd=5,
            mean=datetime.date(1970,3,1),
            min=min,
            max=max,
            use_years=True
        )
    ])

    df = fset.generate_data(5)

    for idx, item in df.iterrows():
        assert item['date']>min and item['date']<max

