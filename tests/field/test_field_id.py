import headfake.field.id
import pytest
from unittest import mock
import datetime

row = {}

class mock_datetime:
    @classmethod
    def now(cls):
        return datetime.date(2020, 3, 24)


def test_IncrementIdGenerator_returns_incremental_values():
    id = headfake.field.id.IncrementIdGenerator(length=2)

    assert ["01","02","03","04","05","06","07"]==[id.select_id() for i in range(1,8)]

def test_IncrementIdGenerator_fails_if_passes_maximum():
    id = headfake.field.id.IncrementIdGenerator(length=2)

    [id.select_id() for i in range(1, 100)]

    with pytest.raises(ValueError,match = r"next number is greater than length"):
        id.select_id()

def test_IdGenerator_is_correct_length():
    id1 = headfake.field.id.IncrementIdGenerator(length=6)
    assert id1.select_id() == "000001"
    assert id1.select_id() == "000002"

    id1 = headfake.field.id.IncrementIdGenerator(length=4)
    assert id1.select_id() == "0001"
    assert id1.select_id() == "0002"

def test_RandomNoReuseIdGenerator_generates_random_no_with_no_replacement(monkeypatch):
    id = headfake.field.id.RandomNoReuseIdGenerator(length=3)

    monkeypatch.setattr("random.randrange",mock.Mock(side_effect=[5,8,4,6,5,9]))
    assert id.select_id() == "005"
    assert id.select_id() == "008"
    assert id.select_id() == "004"
    assert id.select_id() == "006"
    assert id.select_id() == "009"

def test_RandomNoReuseIdGenerator_generates_random_no_with_replacement(monkeypatch):
    id = headfake.field.id.RandomReuseIdGenerator(length=3)

    monkeypatch.setattr("random.randrange",mock.Mock(side_effect=[5,8,4,6,5,9]))
    assert id.select_id() == "005"
    assert id.select_id() == "008"
    assert id.select_id() == "004"
    assert id.select_id() == "006"
    assert id.select_id() == "005"
    assert id.select_id() == "009"

def test_IdField_returns_values_from_id_field_type_with_suffix_and_prefix():
    id_generator = mock.MagicMock(headfake.field.id.IncrementIdGenerator)
    id_generator.select_id.side_effect = ["003","006","005","008","004"]

    id = headfake.field.id.IdField(prefix="P", suffix="S", generator=id_generator)

    assert id.next_value(row) == "P003S"
    assert id.next_value(row) == "P006S"
    assert id.next_value(row) == "P005S"
    assert id.next_value(row) == "P008S"
    assert id.next_value(row) == "P004S"
