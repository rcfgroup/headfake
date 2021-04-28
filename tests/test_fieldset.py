from headfake import HeadFake, Fieldset


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
                     "class":"headfake.field.ConstantField",
                     "value":"2020-03-10"
                     }
                ]
            }
    }

    hf = HeadFake(data)
    assert isinstance(hf.fieldset, Fieldset)
    assert isinstance(hf.fieldset.fields, list)
    assert isinstance(hf.fieldset.field_map, dict)


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
