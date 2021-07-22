import pandas as pd
from datetime import date, datetime as dt

def test_OperationField_example1_generates_discharge_date():
    tpl = {
        "fieldset": {
            "class": "headfake.Fieldset",
            "fields": [
                {
                    "name": "admission_date",
                    "class": "headfake.field.DateField",
                    "min": "2020-01-01",
                    "max": "2020-12-31",
                    "distribution": "scipy.stats.norm",
                    "mean": "2020-06-01",
                    "sd": 30,
                    "min_format": "%Y-%m-%d",
                    "max_format": "%Y-%m-%d",
                    "mean_format": "%Y-%m-%d"
                },
                {
                    "name": "length_of_stay",
                    "class": "headfake.field.NumberField",
                    "min": 18,
                    "max": 80,
                    "distribution": "scipy.stats.norm",
                    "mean": 50,
                    "sd": 15,
                    "dp": 0,
                    "transformers": [
                        {
                            "class": "headfake.transformer.ConvertToDaysDelta"
                        }
                    ],
                    "final_transformers": [
                        {
                            "class": "headfake.transformer.GetProperty",
                            "prop_name": "days"
                        }
                    ]
                },
                {
                    "name": "discharge_date",
                    "class": "headfake.field.OperationField",
                    "operator": "operator.add",
                    "first_value": {
                        "class": "headfake.field.LookupField",
                        "field": "admission_date"
                    },
                    "second_value": {
                        "class": "headfake.field.LookupField",
                        "field": "length_of_stay"
                    },
                    "final_transformers": [
                        {
                            "class": "headfake.transformer.FormatDateTime",
                            "format": "%Y-%m-%d"
                        }
                    ]
                }
            ]
        }
    }
    from headfake import HeadFake

    hf = HeadFake(tpl)
    dset = hf.generate(20)
    assert isinstance(dset, pd.DataFrame)
    assert isinstance(dt.strptime(dset.discharge_date[0], "%Y-%m-%d"), date)

def test_OperationField_example2_generates_discharge_date():
    fields = [
        {
            "name": "admission_date",
            "class": "headfake.field.DateField",
            "min": "2020-01-01",
            "max": "2020-12-31",
            "distribution": "scipy.stats.norm",
            "mean": "2020-06-01",
            "sd": 30,
            "min_format": "%Y-%m-%d",
            "max_format": "%Y-%m-%d",
            "mean_format": "%Y-%m-%d"
        },
        {
            "name": "discharge_date",
            "class": "headfake.field.OperationField",
            "operator": "operator.add",
            "first_value": {
                "class": "headfake.field.LookupField",
                "field": "admission_date"
            },
            "second_value": {
                "class": "headfake.field.NumberField",
                "min": 18,
                "max": 80,
                "distribution": "scipy.stats.norm",
                "mean": 50,
                "sd": 15,
                "dp": 0,
                "transformers": [
                    {
                        "class": "headfake.transformer.ConvertToDaysDelta"
                    }
                ]
            },
            "final_transformers": [
                {
                    "class": "headfake.transformer.FormatDateTime",
                    "format": "%Y-%m-%d"
                }
            ]
        }
    ]
    from headfake import HeadFake

    hf = HeadFake({"fieldset":{"class":"headfake.fieldset.Fieldset","fields":fields}})
    dset = hf.generate(20)
    assert isinstance(dset, pd.DataFrame)
    assert isinstance(dt.strptime(dset.discharge_date[0], "%Y-%m-%d"), date)

