# HEADFAKE

![](https://github.com/rcfgroup/headfake/workflows/main/badge.svg)

## What is HEADFAKE?
**HEA**lth **D**ata **F**aker is a Python-based package which allows the user to create fake or test data sets as described through a YAML-based config file. The package can be embedded directly into Python scripts, or it can be used through a command-line script.

Additionally a version of the package is available through our group web site at https://headfake.rcfgroup.org. This includes limitations on the number of lines which can be generated (maximum 10,000) and only includes the features available within the `headfake` package.


## Why would I use HEADFAKE?
HEADFAKE makes it simple and straightforward to generate fake or test data. It has a number of features which make this easier:

* Support for shareable template-based config or direct Python implementation to setup and perform the data generation.

* Generation of names and contact details through use of the Python package [Faker](https://faker.readthedocs.io/en/master/index.html).

* A selection of fields to handle generation of different types of data.

* Use of the library to embed mock data generation into your own projects (either using a YAML config or constructing the classes manually).

* Basic fields are provided for constant values and to combine values from multiple fields into a single field.

* Randomised names can be output based on a gender field.

* Field data can be looked up from another file using a key field, allowing re-use of patient details in a different field set.

* More realistic simulated data uses statistical distributions to create date of birth and also probability-based option values. Other approaches to simulate real data are also being investigated.

* Clinical data supported includes random NHS numbers and deceased flags/date of death based on age-based odds of death.

* Dependent fields (e.g. one field's values are dependent on the values from one or more)

* Easily create and use custom fields to generate your own data types and values

## How do I install and use HEADFAKE?
To install HEADFAKE please go to the [Installation](installation.md) page and then start with the [Tutorials](tutorials/tutorial1.md) or the [usage page](usage.md).

## Is HEADFAKE being actively maintained?
Yes, we are using HEADFAKE is our own projects and as result are keep it maintained and adding new features when we need them.

## Is HEADFAKE suitable for my project?
The library has been released under an MIT license so can be embedded into your own tools with no restrictions on use.

## If I use HEADFAKE to generate data in my research project which source should I cite?
We are working on a journal paper, for now please cite the project URL (https://rcfgroup.org/headfake).

