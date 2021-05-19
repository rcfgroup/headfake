"""
This package includes fieldset classes
"""

import pandas as pd
from headfake.field import Field

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
            self.fields = fields
            self.field_map = {self._get_name(f): f for f in fields}
        else:
            for field_name, field in fields.items():
                if hasattr(field,"name") and field.name!= field_name:
                    field.name = field_name

            self.fields = list(fields.values())
            self.field_map = fields

        self.field_names = list(self.field_map.keys())

        for field in self.fields:
            if not hasattr(field, "init_from_fieldset"):
                continue

            field.init_from_fieldset(self)


    def _get_name(self, field):
        if hasattr(field,"name"):
            return field.name

        return field.get("name")

    def generate_data(self, num_rows):
        """
        Generates data based on the fields and parameters in this fieldset and return as a pandas dataframe

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe

        """
        dataset = pd.DataFrame(columns=self.field_names)

        generate_funcs = []
        after_funcs = []
        for field in self.fields:
            if field.generate_after is True:
                after_funcs.append((field.name, field.next_value))
            else:
                generate_funcs.append((field.name, field.next_value))

        generate_funcs.extend(after_funcs)

        for i in range(num_rows):
            row = {}
            for field_name, generate_fn in generate_funcs:
                next_val = generate_fn(row)
                if isinstance(next_val, dict):
                    row.update(next_val)
                else:
                    row[field_name] = next_val

            dataset = dataset.append(row, ignore_index=True)

        return dataset

