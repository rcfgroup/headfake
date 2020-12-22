import pandas as pd

class Fieldset:
    def __init__(self, fields, **kwargs):
        self.fields = fields

    def generate_data(self, num_rows):
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


