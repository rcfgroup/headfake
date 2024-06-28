"""
This package includes fieldset classes
"""

import pandas as pd

from headfake.error import NoMoreRows
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
            field.init_transformers(self)

    def _get_name(self, field):
        if hasattr(field,"name"):
            return field.name

        return field.get("name")


    def generate_row(self, compiled_fieldset, input_row=None, **kwargs):
        """
        Generate row values by i) iterating through generation functions for each row, ii) removing hidden fields from
        row and iii) iterating through final transformer functions. If input_row is provided, this is used as the
        starting dictionary.


        Args:
            generation_funcs:
            hidden_fields:
            final_transform_fn_by_name:
            input_row:

        Returns:
            Dictionary of generated field values

        """
        if not input_row:
            input_row = {}

        for field_name, generate_fn in compiled_fieldset.generation_funcs:
            next_val = generate_fn(input_row, **kwargs)
            if isinstance(next_val, dict):
                input_row.update(next_val)
            else:
                input_row[field_name] = next_val

        for hidden in compiled_fieldset.hidden_fields:
            del (input_row[hidden])

        for field_name, final_transformer_fn in compiled_fieldset.final_transform_fn_by_name.items():
            input_row[field_name] = final_transformer_fn(row=input_row, value=input_row[field_name])

        return input_row


    def generate_data(self, num_rows, **kwargs):
        """
        Generates data based on the fields and parameters in this fieldset and return as a pandas dataframe

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe

        """

        data_rows = []
        compiled_fieldset = CompiledFieldset(self)
        for i in range(num_rows):
            try:
                row = self.generate_row(compiled_fieldset, **kwargs)
                data_rows.append(row)
            except NoMoreRows:
                break

        dataset = pd.DataFrame.from_records(data=data_rows, columns=self.field_names, index=None)

        return dataset

class CompiledFieldset:
    def __init__(self, fieldset):
        self.generation_funcs = self._build_generation_functions(fieldset)

        self.hidden_fields = list([f.name for f in filter(lambda x: x.hidden, fieldset.fields)])
        self.final_transform_fn_by_name = self._build_final_transformer_functions(fieldset)

    def _build_generation_functions(self, fieldset):
        """
        Build list of field generation functions with those which need to run after all other functions to the end.
        """

        generation_funcs = []
        after_funcs = []
        for field in fieldset.fields:
            if field.generate_after is True:
                after_funcs.append((field.name, field.next_value))
            else:
                generation_funcs.append((field.name, field.next_value))


        generation_funcs.extend(after_funcs)

        return generation_funcs

    def _build_final_transformer_functions(self, fieldset):
        final_transform_fn_by_name = {}

        for field in fieldset.fields:
            if field.final_transformers and not field.hidden:
                final_transform_fn_by_name[field.name] = partial(transform_value, field=field,
                                                                 transformers=field.final_transformers)
        return final_transform_fn_by_name


from functools import partial
