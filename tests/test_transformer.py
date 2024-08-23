import headfake.error
from headfake import transformer as T
from headfake.field import ConstantField, LastNameField, GenderField, TextField, LookupField
from headfake.fieldset import Fieldset
from datetime import datetime, date, timezone as tz, timedelta as td
import numpy as np
import pytest
import random

def test_field_with_transformers_set_to_none():
    txt = TextField(transformers=None)
    txt.next_value({})

def test_upper_case_transformer():
    constant = ConstantField(value="my_constant", transformers = [T.UpperCase()])
    assert constant.next_value({}) == "MY_CONSTANT"

def test_SplitPiece_transformer_returns_first_bit_from_split_string():
    tfield = LookupField(field="second_bit", transformers=[
        T.SplitPiece(separator=";", index=1)
    ])
    assert tfield.next_value({"second_bit":"A;B;C;D"}) == "B"
    assert tfield.next_value({"second_bit": "X;Y;Z"}) == "Y"
    assert tfield.next_value({"second_bit": ""}) is ""

def test_ReformatDateTime_returns_reformatted_date_from_date_string_and_handles_errors():
    dfield = LookupField(field="source_date", transformers=[
        T.ReformatDateTime(source_format="%Y-%m-%d", target_format="%d/%m/%Y")
    ])
    assert dfield.next_value({"source_date":"2021-03-04"}) == "04/03/2021"
    assert dfield.next_value({"source_date": "1956-12-31"}) == "31/12/1956"

    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"source_date": "03/04/21"})

def test_ConvertStrToDate_returns_date_object_from_date_string_and_handles_errors():
    dfield = LookupField(field="date", transformers=[
        T.ConvertStrToDate(format="%Y-%m-%d")
    ])
    assert dfield.next_value({"date":"2021-03-04"}) == date(day=4,month=3,year=2021)
    assert dfield.next_value({"date": "1956-12-31"}) == date(day=31,month=12,year=1956)
    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"date": "03/04/21"})

def test_ConvertStrToDateTime_returns_datetime_object_from_datetime_string_and_handles_errors():
    dfield = LookupField(field="ts", transformers=[
        T.ConvertStrToDateTime(format="%Y-%m-%d %H:%M")
    ])
    assert dfield.next_value({"ts":"2021-03-04 12:42"}) == datetime(day=4,month=3,year=2021, hour=12, minute=42, tzinfo=tz.utc)
    assert dfield.next_value({"ts": "1956-12-31 14:54"}) == datetime(day=31, month=12, year=1956, hour=14, minute=54, tzinfo=tz.utc)

    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"ts": "1956-12-31"})

    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"ts": "03/04/21 12:45"})

def test_ConvertToNumber_with_as_integer_flag_returns_integer_from_string_and_handles_errors():
    dfield = LookupField(field="los", transformers=[
        T.ConvertToNumber(as_integer=True)
    ])
    assert dfield.next_value({"los":"1234"}) == int(1234)
    assert dfield.next_value({"los": 1234}) == int(1234)

    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"los": "1234x"})

def test_ConvertToNumber_with_no_as_integer_flag_returns_float_from_string_and_handles_errors():
    dfield = LookupField(field="los", transformers=[
        T.ConvertToNumber(as_integer=False)
    ])
    assert dfield.next_value({"los":"1234.56"}) == np.float32(1234.56)
    assert dfield.next_value({"los": 1234.56}) == np.float32(1234.56)

    with pytest.raises(headfake.error.TransformerError):
        assert dfield.next_value({"los": "1234x"})

def test_FormatNumber_returns_string_from_number_and_handles_errors():
    dfield = LookupField(field="los", transformers=[
        T.FormatNumber(dp=1)
    ])
    assert dfield.next_value({"los":1234.56}) == "1234.6"
    assert dfield.next_value({"los": 1234.54}) == "1234.5"

def test_ConvertToDaysDelta_returns_timedelta_object_from_number_and_handles_errors():
    dfield = LookupField(field="los", transformers=[
        T.ConvertToDaysDelta()
    ])
    assert dfield.next_value({"los":5}) == td(5)
    assert dfield.next_value({"los":56}) == td(56)


def test_GetProperty_returns_specified_property_from_object():
    dfield = LookupField(field="los", transformers=[
        T.GetProperty(prop_name="__class__"),
        T.GetProperty(prop_name="__name__")
    ])
    assert dfield.next_value({"los":5}) == "int"
    assert dfield.next_value({"los":"5"}) == "str"
    assert dfield.next_value({"los": None}) == "NoneType"

def test_GetProperty_returns_error_if_the_property_does_not_exist():
    dfield = LookupField(field="los", transformers=[
        T.GetProperty(prop_name="notaproperty")
    ])

    with pytest.raises(headfake.error.TransformerError):
        dfield.next_value({"los": 5})

def test_FormatDateTime_returns_string_from_date_and_datetime_and_handles_errors():
    dfield = LookupField(field="timestamp", transformers=[
        T.FormatDateTime(format="%Y-%m-%d")
    ])
    assert dfield.next_value({"timestamp":datetime(day=4,month=3,year=2021, hour=12, minute=42, tzinfo=tz.utc)}) == "2021-03-04"
    assert dfield.next_value({"timestamp": date(day=31,month=12,year=1956)}) == "1956-12-31"

def test_IntermittentBlanks_returns_empty_strings_and_values():
    random.seed(123)
    tfield = LookupField(field="my_value", transformers=[
        T.IntermittentBlanks(blank_probability=0.3,blank_value="")
    ])
    assert tfield.next_value({"my_value":5}) == ''
    assert tfield.next_value({"my_value": 5}) == ''
    assert tfield.next_value({"my_value": 5}) == 5
    assert tfield.next_value({"my_value": 5}) == ''