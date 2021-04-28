"""
This package includes fieldset classes
"""

import pandas as pd


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
            self.field_map = {f.name: f for f in fields}
        else:
            self.fields = list(fields.values())
            self.field_map = fields

    def generate_data(self, num_rows):
        """
        Generates data based on the fields and parameters in this fieldset and return as a pandas dataframe

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe

        """
        dataset = pd.DataFrame()

        for i in range(num_rows):
            row = {}
            for field in self.fields:
                next_val = field.next_value(row)
                if isinstance(next_val, dict):
                    row.update(next_val)
                else:
                    row[field.name] = next_val

            dataset = dataset.append(row, ignore_index=True)

        return dataset
