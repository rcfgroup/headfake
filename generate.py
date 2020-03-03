from mockd.util import config_from_yaml_file, create_class_tree
import csv

conf = config_from_yaml_file("uhl_patients.yaml")

print(conf)

no_rows = 1000
output_file = "test.txt"
with open(output_file, "w") as out:
    writer = csv.DictWriter(out, list(conf.get("fields").keys()))
    writer.writeheader()
    for row_no in range(1,no_rows):
        row={}
        for fname, field in conf.get("fields",{}).items():
            row[fname] = field.next_value()

        writer.writerow(row)