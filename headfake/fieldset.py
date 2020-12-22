"""
This file implements the Fieldset class
"""

import pandas as pd

class Fieldset:
    """
    A Fieldset object defines the parameters for the data generation process
    """

    def __init__(self, fields, **kwargs):
        """
        constructor

        Args:
            fields: specification of fields in this fieldset
            **kwargs: dictionary of keyword arguments
        """

        self.fields = fields


    def generate_data(self, num_rows):
        """
        generate data based on the parameters of this fieldset and return as a pandas dataframe

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe

        """
        dataset = pd.DataFrame()

        for i in range(num_rows):
            row = {}
            for fname, field in self.fields.items():
                next_val = field.next_value(row)
                if isinstance(next_val, dict):
                    row.update(next_val)
                else:
                    row[fname] = next_val

            dataset = dataset.append(row, ignore_index=True)

        return dataset


