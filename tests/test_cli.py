import attr
import csv
import os
import tempfile

from headfake.cli import Command

@attr.s
class Args:
    template = attr.ib()
    output_file = attr.ib()
    no_rows = attr.ib()

    def as_list(self):
        return [
            "--output-file",
            self.output_file,
            "--no-rows",
            str(self.no_rows),
            self.template
        ]

def test_generate_patients_data_from_template():
    with tempfile.NamedTemporaryFile(mode="w",delete=False) as tmp:
        tmp.write(" ")
        tmp.close()
        args = Args(template = "examples/patients.yaml", no_rows = 20, output_file = str(tmp.name))

        Command.run(args.as_list())

        assert os.path.exists(tmp.name) is True

        with open(tmp.name,"r") as fh:
            file = csv.DictReader(fh)
            lines = list(file)

        assert len(lines) == 20

        os.unlink(tmp.name)


def test_generate_screening_data_from_template():
    with tempfile.NamedTemporaryFile(mode="w",delete=False) as tmp:
        tmp.write(" ")
        tmp.close()
        args = Args(template = "examples/screening.yaml", no_rows = 20, output_file = str(tmp.name))

        Command.run(args.as_list())

        assert os.path.exists(tmp.name) is True

        with open(tmp.name,"r") as fh:
            file = csv.DictReader(fh)
            lines = list(file)

        assert len(lines) == 20

        os.unlink(tmp.name)
