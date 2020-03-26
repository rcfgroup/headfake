# HEADFAKE

![](https://github.com/rcfgroup/headfake/workflows/main/badge.svg)

**HEA**lth **D**ata **F**aker provides a package and command-line scripts to create mock data files based on a YAML-based config file (see examples for example templates). It use the Python Faker package to provide generated names and contact details.

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
Python 3.6+ only supported. The best thing to do at the moment is to create and activate a virtual environment in the package path.

```bash
python3 -m venv venv
source venv/bin/activate
```
Install requirements using pip:
```bash
pip install -r requirements.txt
```

Then try running the script on one of the examples:
```bash
python generate-fake-data.py examples/patients.yaml --no-rows=100
```

This should generate 100 rows of example data. Using an --output-file flag will send it to a file rather than to the screen.

# Future development
- [ ] Support for clinical coding systems (e.g. ICD10, READ, SNOMED-CT)
- [ ] Dependent fields (e.g. one field's values are dependent on the values from one or more)
- [ ] Multiple interlinked fieldsets
- [ ] Specific ordering of output fields
