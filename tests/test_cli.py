import attr
import os
import tempfile
from headfake.cli import generate_from_args
import csv
import random
@attr.s
class Args:
    template = attr.ib()
    output_file = attr.ib()
    no_rows = attr.ib()

def test_generate_patients_data_from_template():
    with tempfile.NamedTemporaryFile(mode="w",delete=False) as tmp:
        tmp.write(" ")
        tmp.close()
        args = Args(template = os.path.dirname(__file__) + "/../examples/patients.yaml", no_rows = 50, output_file = str(tmp.name))

        generate_from_args(args)

        assert os.path.exists(tmp.name) is True

        with open(tmp.name,"r") as fh:
            file = csv.DictReader(fh)
            lines = list(file)

        assert len(lines) == 50


        os.unlink(tmp.name)

def test_generate_screening_data_from_template():
    with tempfile.NamedTemporaryFile(mode="w",delete=False) as tmp:
        tmp.write(" ")
        tmp.close()
        args = Args(template = os.path.dirname(__file__) + "/../examples/screening.yaml", no_rows = 100, output_file = str(tmp.name))

        generate_from_args(args)

        assert os.path.exists(tmp.name) is True

        with open(tmp.name,"r") as fh:
            file = csv.DictReader(fh)
            lines = list(file)

        assert len(lines) == 100

        os.unlink(tmp.name)
