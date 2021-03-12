**HEA**lth **D**ata **F**aker is a Python-based package and command-line script which allows the user to create mock data files described through a YAML-based config file.

Key features include:

* Generation of names and contact details through use of the Python package [Faker](https://faker.readthedocs.io/en/master/index.html).

* A selection of fields to handle generation of different types of data.

* Template-based config which automatically constructs the Python class tree
in order to then perform the data generation.

* Use of the library to embed mock data generation into your own projects (either using a YAML config or constructing the classes manually).

* Basic fields are provided for constant values and to combine values from multiple fields into a single field.

* Randomised names can be output based on a gender field.

* Field data can be looked up from another file using a key field, allowing re-use of patient details in a different field set.

* More realistic simulated data uses statistical distributions to create date of birth and also probability-based option values. Other approaches to simulate real data are also being investigated.

* Clinical data supported includes random NHS numbers and deceased flags/date of death based on age-based odds of death.

* Dependent fields (e.g. one field's values are dependent on the values from one or more)

* Easily create and use custom fields to generate your own data types and values
