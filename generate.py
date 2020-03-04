from mockd.util import config_from_yaml_file, create_class_tree
import csv
import pprint
conf = config_from_yaml_file("uhl_patients.yaml")
pprint.pprint(conf)
fset = conf.get("fieldset")
for fname, field in fset.fields.items():
    field.fieldset = fset

no_rows = 1000
output_file = "test.txt"
with open(output_file, "w") as out:
    writer = csv.DictWriter(out, list(fset.fields.keys()))
    writer.writeheader()
    for row_no in range(1,no_rows):
        row={}
        for fname, field in fset.fields.items():
            row[fname] = field.next_value(row)

        writer.writerow(row)