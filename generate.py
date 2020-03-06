from mockd.util import config_from_yaml_file, create_class_tree
import csv
import pprint
conf = config_from_yaml_file("uhl_patients.yaml")
pprint.pprint(conf)
fset = conf.get("fieldset")
for fname, field in fset.fields.items():
    field.init_from_fieldset(fset)

no_rows = 1000
output_file = "test.txt"
with open(output_file, "w") as out:
    fieldnames = []
    for field in fset.fields.values():
        fieldnames.extend(field.names)
    print("fieldnames:" + str(fieldnames))
    writer = csv.DictWriter(out, fieldnames)
    writer.writeheader()
    for row_no in range(1,no_rows):
        row={}
        for fname, field in fset.fields.items():
            next_val = field.next_value(row)
            if isinstance(next_val, dict):
                row.update(next_val)
            else:
                row[fname] = next_val

        writer.writerow(row)