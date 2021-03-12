# HEADFAKE

![](https://github.com/rcfgroup/headfake/workflows/main/badge.svg)

**HEA**lth **D**ata **F**aker provides a package and command-line scripts to create mock data files based on a YAML-based config file (see examples for example templates). It uses the Python package [Faker](https://faker.readthedocs.io/en/master/index.html) to provide generated names and contact details.

Key features include:

* Extensible field types to handle generation of different types of data.

* Template-based config which automatically constructs the Python class tree
in order to then perform the data generation.

* Use of the library to embed mock data generation into your own projects (either using a YAML config or constructing the classes manually).

* Basic fields are provided for constant values and to combine values from multiple fields into a single field.

* Randomised names can be output based on a gender field.

* Field data can be looked up from another file using a key field, allowing re-use of patient details in a different field set.

* More realistic simulated data uses statistical distributions to create date of birth and also probability-based option values. Other approaches to simulate real data are also being investigated.

* Clinical data supported includes random NHS numbers and deceased flags/date of death based on age-based odds of death.

More comprehensive documentation is in progress. As it stands there are probably more efficient ways to generate some of the data (e.g. the age simulation could be done using bayesian approaches with prior odds).

# Installation

This package requires Python 3.6 or above. In your virtual environment, install the package from github:

```bash
pip install git+ssh://git@github.com/rcfgroup/headfake.git
```

# Command Line Usage

You can run `headfake` from the command line without writing any code. 

```
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
                        Output data to file rather than STDOUT
  -n NO_ROWS, --no-rows NO_ROWS
                        Number of rows to generate
  -s SEED, --seed SEED  Seed for the random data generator
````

You can either write your own template or use one from the examples directory as shown below:

```bash
headfake examples/patients.yaml --no-rows=100
```

This should generate 100 rows of example data. Using an --output-file flag will send it to a file rather than to the screen.  

# API

HEADFake provides an API that you can use in your python code to generate data. The following code loads the `patients.yaml` template and is equivalent to the command line interface shown above.

```python
from headfake import HeadFake

headfake = HeadFake.from_yaml("examples/patients.yaml")
data = headfake.generate(num_rows=100)
```

The return value from `HeadFake.generate` is a [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)

# Development

If you're developing this package, you can install it using pip as shown below: 

```bash
pip install -e ".[tests]"
```

# Building the documentation
To build the documentation you can install dependencies using pip as shown below:
```bash
pip install -e ".[docs]"
```
Then to build the docs it should be as simple as running:
```bash
mkdocs build
```

# Future development
- [ ] Support for clinical coding systems (e.g. ICD10, READ, SNOMED-CT)
- [ ] Dependent fields (e.g. one field's values are dependent on the values from one or more)
- [ ] Multiple interlinked fieldsets
- [ ] Specific ordering of output fields
