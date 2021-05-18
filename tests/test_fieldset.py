from headfake import HeadFake, Fieldset
from headfake.field import IdField


def test_Fieldset_can_accept_list_of_fields_as_input():
    data = {
        "fieldset":
            {
                "class": "headfake.fieldset.Fieldset",
                "fields": [
                    {"name":"spell_id",
                     "class":"headfake.field.IdField",
                     "prefix":"SPL",
                     "generator":{
                         "class":"headfake.field.IncrementIdGenerator",
                         "length":6,
                         "min_value":1000000
                     },
                    },
                    {"name":"admission_date",
                     "value":"2020-03-10"
                     },
                    {"name": "discharge_date",
                     "value": "2020-03-15"
                     },
                    {"name": "comments",
                     "class":"headfake.field.TextField",
                     "max_length":30
                     }
                ]
            }
    }

    hf = HeadFake(data)
    assert isinstance(hf.fieldset, Fieldset)
    assert isinstance(hf.fieldset.fields, list)
    assert list(hf.fieldset.field_map.keys()) == ["spell_id","admission_date","discharge_date","comments"]

def test_Fieldset_can_accept_constant_values_in_list_form():
    data = {
        "fieldset":
            {
                "class": "headfake.fieldset.Fieldset",
                "fields": [
                    {"name": "discharge_date",
                     "value": "2020-03-15"
                     }
                ]
            }
    }

    hf = HeadFake(data)


def test_Fieldset_can_accept_a_dictionary_of_fields_as_input():
    data = {
        "fieldset":
            {
                "class": "headfake.fieldset.Fieldset",
                "fields": {
                    "spell_id":{
                         "class":"headfake.field.IdField",
                         "prefix":"SPL",
                         "generator":{
                             "class":"headfake.field.IncrementIdGenerator",
                             "length":6,
                             "min_value":1000000
                         },

                    },
                    "admission_date": {
                         "class":"headfake.field.ConstantField",
                         "value":"2020-03-10"
                }
            }
            }
    }

    hf = HeadFake(data)
    assert isinstance(hf.fieldset, Fieldset)
    assert isinstance(hf.fieldset.fields, list)
    assert isinstance(hf.fieldset.field_map, dict)
    assert isinstance(hf.fieldset.field_map["spell_id"],IdField)
    assert hf.fieldset.field_map["spell_id"].name == "spell_id"
