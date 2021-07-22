# Headfake

## What is Headfake?
**Hea**lth **d**ata **fake**r is a Python-based package which allows the user to use a declarative approach to create fake or test data sets.
using either Python code, or a YAML or JSON template file.

The package can be embedded directly into Python scripts, or it can be used through the command-line.

It takes ideas from other declarative packages (e.g. pydbgen), but also adds support for a number of additional features
including: statistically distributed random values; dependent fields and custom fields as well as approaches for
transforming generated fields before/after the generation process.

## How do I install and use Headfake?
To get started quickly, you can use pip to install it:
```bash
pip install headfake
```

Then test it out using one of the example YAML templates:
```bash
headfake examples/patients.yaml --no-rows=100
```

You should get 100 rows of generated data.

For further information on using Headfake head over to the [Tutorials](tutorials/tutorial1) or the [Usage](usage) page.

## Why would I use Headfake?
Headfake makes it simple and straightforward to generate fake or test data. It has a number of features which make this easier:

* Support for shareable template-based config or direct Python implementation to setup and perform the data generation.

* Embeddable data generation into projects (either using a YAML/JSON config or using Python data structures/classes).

* Generation of names and contact details through use of the Python package Faker

* Randomised names can be output based on a gender field.

* More realistic simulated data uses statistical distributions to create date of birth and also probability-based option values. Other approaches to simulate real data are also being investigated.

* Clinical data supported includes random NHS numbers and deceased flags/date of death based on age-based odds of death.

* Dependent fields (e.g. one field's values are dependent on the values from one or more)

* Combined operation fields (e.g. combine generated values using specific operations such as add or subtract)

* Field data can be looked up from another file using a key field, allowing re-use of patient details in a different field set.

* A selection of fields to handle generation of different types of data.

* Ability to create and use custom fields to generate your own data types and values

* Support for transformers which process data once it's been generated or just before it is output.

## Is Headfake being actively maintained?
Yes, we are using Headfake is our own projects and as result are keep it maintained and adding new features when we need them.

## Is Headfake suitable for my project?
The library has been released under an MIT license so can be embedded into your own tools with minimal restrictions on use.

## If I use Headfake to generate data in my research project which source should I cite?
We are working on a journal paper, for now please cite the project URL (https://rcfgroup.github.io/headfake).

