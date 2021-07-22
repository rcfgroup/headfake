import pytest

from headfake.util import create_class_tree
from headfake.field import TextField, IfElseField, ConstantField
from headfake.fieldset import Fieldset

def test_class_tree_from_field_dict_with_constant_is_created_correctly():

    tree = create_class_tree(None, {"discharge_date": "2020-03-15"})

    assert tree == {'discharge_date': "2020-03-15"}

def test_class_tree_from_field_list_with_constant_is_created_correctly():

    tree = create_class_tree(None, [{"name":"discharge_date", "value":"2020-03-15"}])

    assert tree == [{"name":"discharge_date", "value":"2020-03-15"}]

def test_nested_class_tree_with_constant_is_created_correctly():

    tree = create_class_tree(None, {"fieldset":{"fields":[{"name":"discharge_date", "value":"2020-03-15"},{"name":"comment","class":"headfake.field.TextField", "max_length":50}],"class":"headfake.fieldset.Fieldset"}})

    assert isinstance(tree.get("fieldset"),Fieldset)
    fields = tree.get("fieldset").fields

    ddate = fields[0]
    assert ddate.name == "discharge_date"
    assert ddate.value == "2020-03-15"
    assert isinstance(ddate, ConstantField)

    assert isinstance(fields[1],TextField)
    assert fields[1].name == "comment"
    assert fields[1].max_length == 50

def test_class_tree_with_dictionary_with_incorrect_class_raises_exception():
    with pytest.raises(TypeError):
        create_class_tree(None, {
            "title": {
                "class": "headfake.field.IfElseField",
                "condition": {
                    "field": "gender",
                    "operator": "operator.equal",
                    "value": "M"
                },
                "true_value": "MR",
                "false_value": "MRS"
            }
        })

