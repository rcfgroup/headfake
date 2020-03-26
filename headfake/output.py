import csv
import sys
from abc import ABC

class Output(ABC):
    """
    Base output class.
    """
    def __init__(self, options):
        """
        Setup output with appropriate options.
        :param options: Arguments dictionary
        """
        self.options = options

    def _open(self, fieldset):
        """
        Open/setup output.
        :param fieldset:
        :return:
        """
        pass

    def _close(self):
        """
        Close/teardown output
        :return:
        """
        pass

    def write_fieldset(self, fieldset):
        """
        Main method used to write a single fieldset to the output.
        :param fieldset:
        :return:
        """
        self._open(fieldset)

        try:
            for row_no in range(0, self.options.no_rows):
                row = {}
                for fname, field in fieldset.fields.items():
                    next_val = field.next_value(row)
                    if isinstance(next_val, dict):
                        row.update(next_val)
                    else:
                        row[fname] = next_val

                self._write_row(row)
        finally:
            self._close()

    def _write_row(self):
        pass


class FileOutput(Output):
    """
    Output generated mock data for a single fieldset to the tab-delimited text file specified in the options (output_file)
    """
    @property
    def filehandle(self):
        return open(self.options.output_file, "w")

    def _open(self, fieldset):
        self.fh = self.filehandle

        fieldnames = []
        for field in fieldset.fields.values():
            fieldnames.extend(field.names)

        self.writer = csv.DictWriter(self.fh, fieldnames)
        self.writer.writeheader()

    def _close(self):
        self.fh.close()

    def _write_row(self, row):
        self.writer.writerow(row)


class StdoutOutput(FileOutput):
    """
    Output generated mock data for a single fieldset to the console/STDOUT
    """
    @property
    def filehandle(self):
        return sys.stdout

    def _close(self):
        pass


class InternalOutput(Output):
    """
    Output generated mock data to an internal property (rows). Used for embedding the lock from headfake into
    other modules.
    """
    def __init__(self, options):
        super().__init__(options)
        self.rows = []

    def _write_row(self, row):
        self.rows.append(row)
