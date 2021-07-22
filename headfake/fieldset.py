"""
This package includes fieldset classes
"""

import pandas as pd
from headfake.field import Field, transform_value, ConstantField

import logging

def is_field_shown(field):
    if isinstance(field, Field):
        return not field.hidden

    return True

def obtain_name(field):
    if isinstance(field, Field):
        return field.name

    return field["name"]

def coerce_into_field(field_data, field_name=None):
    if issubclass(field_data.__class__, Field):
        if field_name and hasattr(field_data, "name") and field_data.name != field_name:
            field_data.name = field_name

        return field_data

    field_name = field_data.get("name") if isinstance(field_data,dict) else field_name
    if isinstance(field_data, dict) and list(field_data.keys()) == ["name","value"]:
        field_value = field_data.get("value")
    else:
        field_value = field_data

    return ConstantField(name=field_name, value=field_value)


class Fieldset:
    """
    The basic Fieldset object which contains the fields and parameters for the data generation process.
    """

    def __init__(self, fields, **kwargs):
        """
        constructor

        Args:
            fields: specification of fields in this fieldset
            **kwargs: dictionary of keyword arguments
        """

        if isinstance(fields, list):
            fields = [coerce_into_field(f) for f in fields]
            self.fields = fields
            self.field_map = dict([(self._get_name(f), f) for f in fields])
        else:
            fields = dict([(fname, coerce_into_field(f, fname)) for fname, f in fields.items()])

            self.fields = list(fields.values())
            self.field_map = fields

        self.field_names = [obtain_name(f) for f in filter(is_field_shown, self.fields)]

        for field in self.fields:
            if not hasattr(field, "init_from_fieldset"):
                continue

            field.init_from_fieldset(self)



    def _get_name(self, field):
        if hasattr(field,"name"):
            return field.name

        return field.get("name")

    def _build_generation_functions(self):
        """
        Build list of field generation functions with those which need to run after all other functions to the end.
        """

        generation_funcs = []
        after_funcs = []
        for field in self.fields:
            if field.generate_after is True:
                after_funcs.append((field.name, field.next_value))
            else:
                generation_funcs.append((field.name, field.next_value))


        generation_funcs.extend(after_funcs)

        return generation_funcs

    def _build_final_transformer_functions(self):
        final_transform_fn_by_name = {}

        for field in self.fields:
            if field.final_transformers and not field.hidden:
                final_transform_fn_by_name[field.name] = partial(transform_value, field=field,
                                                                 transformers=field.final_transformers)
        return final_transform_fn_by_name

    def _generate_row(self, generation_funcs, hidden_fields, final_transform_fn_by_name):
        """
        Generate row values by i) iterating through generation functions for each row, ii) removing hidden fields from
        row and iii) iterating through final transformer functions


        Args:
            generation_funcs:
            hidden_fields:
            final_transform_fn_by_name:

        Returns:
            Dictionary of generated field values

        """
        row = {}
        for field_name, generate_fn in generation_funcs:
            next_val = generate_fn(row)
            if isinstance(next_val, dict):
                row.update(next_val)
            else:
                row[field_name] = next_val

        for hidden in hidden_fields:
            del (row[hidden])

        for field_name, final_transformer_fn in final_transform_fn_by_name.items():
            row[field_name] = final_transformer_fn(row=row, value=row[field_name])

        logging.info(f"row:{row}")
        return row

    def generate_data(self, num_rows):
        """
        Generates data based on the fields and parameters in this fieldset and return as a pandas dataframe

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe

        """
        generation_funcs = self._build_generation_functions()

        hidden_fields = list([f.name for f in filter(lambda x: x.hidden, self.fields)])
        final_transform_fn_by_name = self._build_final_transformer_functions()

        data_rows = []
        for i in range(num_rows):
            row = self._generate_row(generation_funcs, hidden_fields, final_transform_fn_by_name)

            data_rows.append(row)

        dataset = pd.DataFrame.from_records(data=data_rows, columns=self.field_names, index=None)

        logging.info(f"dataset:{dataset}")
        return dataset

from functools import partial
