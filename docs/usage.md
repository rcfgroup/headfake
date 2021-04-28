# Usage

## Command Line

You can run `headfake` from the command line without writing any code.

```text
usage: headfake [-h] [-o OUTPUT_FILE] [-n NO_ROWS] [-s SEED] template

HEAlth Data Faker provides a command-line script to create mock data files based on a YAML-based
template file (see examples/* for example templates). HEADFake uses the python package Faker to
generate names and contact details.

positional arguments:
  template              YAML-based template file describing structure of health data fields to
                        generate

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output data to text file as tab-delimited rather than STDOUT
  -n NO_ROWS, --no-rows NO_ROWS
                        Number of rows to generate
  -s SEED, --seed SEED  Seed for the random data generator
```

You can either write your own template or use one from the examples directory as shown below:

```bash
headfake examples/patients.yaml --no-rows=100
```

This should generate 100 rows of example data. Using an --output-file flag will send it to a tab-delimited file rather than to the screen.

```bash
headfake examples/patients.yaml --no-rows=100 --output-file=examples/patient.txt
```

## Python API

Headfake provides an API that you can use in your python code to generate data. The following code loads the `patients.yaml` template and is equivalent to the command line interface shown above.

```python
from headfake import HeadFake

headfake = HeadFake.from_yaml("examples/patients.yaml")
data = headfake.generate(num_rows=100)
```

The return value from `HeadFake.generate` is a [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)