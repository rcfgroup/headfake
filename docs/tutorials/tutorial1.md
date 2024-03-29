# Tutorial 1. Generate a fake data file

## Aims of tutorial
This tutorial will take you through installing Headfake, creating a Headfake configuration file and using it to generate a data file.

## Install Headfake

You will need at least Python 3.6+ installed in order to use Headfake. The easiest way to install it is through pip. In the terminal enter:

```bash
pip install headfake
```

Check it is installed correctly by running:

```bash
headfake --help
```

You should get some information on the usage of the tool.

## Creating a template file

Headfake is powered through a plain text template file in YAML format. The easiest way to demonstrate its functionality
is to try out an example.

Open a file `tutorial.yml` in your home directory, copy and paste the information below into it and save it:


!!! warning
    Be careful to use EITHER spaces OR tabs to indent the YAML file. If you mix them up then Headfake is likely to throw
    errors. It also important to make the indentation consistent when doing this.

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    - name: main_pat_id
      class: headfake.field.IdField
      prefix: S
      generator:
        class: headfake.field.IncrementIdGenerator
        length: 7
        min_value: 1000000

    - name: gender
      class: headfake.field.GenderField
      male_value: "M"
      female_value: "F"
      male_probability: 0.3

    - name: last_name
      class: headfake.field.LastNameField
      gender_field: gender

    - name: dob
      class: headfake.field.DateOfBirthField
      min: 0
      max: 105
      mean: 45
      sd: 13
      distribution: scipy.stats.norm
      date_format: "%Y-%m-%d"

```


## Generating fake data

Now on the command-line run:

```
headfake /path/to/tutorial1.yml -o /path/to/tutorial1.txt -n100
```

Here you are specifying the template to use, and then an output file (/path/to/tutorial1.txt) and number of rows to generate (100)

If you now open the output file you will see 1000 rows of generated data.

You can also run without the -o option and the data will be output to the screen:
```
headfake /path/to/tutorial1.yml  -n100
```

This latter approach is often better when building templates in Headfake as it more immediate.



## Analysis
This is a simple example of what Headfake can do. It is also possible to use YAML to provide your fields as a dictionary, or to embed it directly as Python data structures and/or code.
There is additional information on different ways for [initialising Headfake](../../discussion/initialising-headfake).

The template you used defines a set of fields containing autogenerated IDs, gender, a last name and a date of birth following a normal distribution.

You can see from this tutorial how straightforward it would be to add additional fields to the template and to generate more/less rows of data.

In the next tutorial we will take a closer look at the setup of the fields in the YAML file and modify them to create different data and formats.
