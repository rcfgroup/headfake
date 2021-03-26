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
        true = "MR",
        false = "MRS"
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
        true="MRS",
        false="MISS"
    )

    gender_if_else = field.IfElseField(
        condition = gender_cond,
        true = "MR",
        false = ms_if_else
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
        true="MRS",
        false=female_ov
    )


    gender_if_else = field.IfElseField(
        condition = gender_cond,
        true = "MR",
        false = ms_if_else
    )

    gender_if_else.init_from_fieldset(fset)

    assert gender_if_else.next_value({"gender":"M","marital_status":"M"}) == "MR"
    assert gender_if_else.next_value({"gender": "M", "marital_status": "S"}) == "MR"
    assert gender_if_else.next_value({"gender":"F","marital_status": "S"}) == "MS"
    assert gender_if_else.next_value({"gender": "F", "marital_status": "S"}) == "MISS"
    assert gender_if_else.next_value({"gender": "F", "marital_status": "S"}) == "PROF"


def test_MultiField_generates_list_of_values():
    random.seed(124)
    gender_field = field.MultiField(
        field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
        min_values=3,
        max_values=7
    )

    assert gender_field.next_value({}) == ['M', 'M', 'F', 'M', 'F']
    assert gender_field.next_value({}) == ['M', 'M', 'M']

def test_MultiField_generates_joined_list_of_values():
    random.seed(124)
    gender_field = field.MultiField(
        field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
        min_values=3,
        max_values=7,
        glue=","
    )

    assert gender_field.next_value({}) == "M,M,F,M,F"
    assert gender_field.next_value({}) == "M,M,M"

def test_MultiField_nested_generates_multiple_joined_list_of_values():
    random.seed(124)
    gender_field = field.MultiField(
        field = field.MultiField(
            field = field.GenderField(male_value="M",female_value="F",male_probability=0.6),
            min_values=3,
            max_values=7,
            glue=","
        ),
        min_values=2,
        max_values=8,
        glue="|"
    )

    assert gender_field.next_value({}) == "M,F,M|M,M,F,F,M|F,M,M,M,M,M|M,F,M,M,F"
    assert gender_field.next_value({}) == "M,M,F|F,M,M|F,F,M,M,F,M|F,M,M,M,M,M|F,M,M|F,M,M"