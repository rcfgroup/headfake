import sys
import csv

class Output:
    def __init__(self,options):
        self.options = options

    def open(self, fieldset):
        pass

    def close(self):
        pass

    def write_fieldset(self, fieldset):
        self.open(fieldset)

        try:
            for row_no in range(1, self.options.no_rows):
                row = {}
                for fname, field in fieldset.fields.items():
                    next_val = field.next_value(row)
                    if isinstance(next_val, dict):
                        row.update(next_val)
                    else:
                        row[fname] = next_val

                self.write_row(row)
        finally:
            self.close()

    def write_row(self):
        pass


class FileOutput(Output):
    @property
    def filehandle(self):
        return open(self.options.output_file, "r")

    def open(self, fieldset):
        self.fh = self.filehandle

        fieldnames = []
        for field in fieldset.fields.values():
            fieldnames.extend(field.names)

        self.writer = csv.DictWriter(self.fh, fieldnames)

    def close(self):
        self.fh.close()

    def write_row(self, row):
        self.writer.writerow(row)

class StdoutOutput(FileOutput):
    @property
    def filehandle(self):
        return sys.stdout

    def close(self):
        pass

class InternalOutput(Output):
    def __init__(self, options):
        super().__init__(options)
        self.rows = []

    def write_row(self,row):
        self.rows.append(row)