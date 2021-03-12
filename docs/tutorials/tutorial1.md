# Tutorial 1. Generate a fake data file

## Aims of tutorial
This tutorial will take you through installing HEADFAKE, creating a HEADFAKE configuration file and using it to generate a data file.

## Install HEADFAKE

You will need at Python 3.6+ installed in order to use HEADFAKE.

The easiest way to install it is through pip. In the terminal enter:


```bash
pip install headfake
```

Check it is installed correctly by running

```bash
headfake --help
```

You should get some information on the usage of the tool.

## Creating a template file

HEADFAKE is powered through a plain text template file in YAML format.
The easiest way to demonstrate its functionality is to try out an example.

Open a file `example.yml` in your home directory and copy and paste the information below into it:

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    main_pat_id:
      class: headfake.field.IdField
      prefix: S
      generator:
        class: headfake.field.IncrementIdGenerator
        length: 7
        min_value: 1000000

      transformers:
        - class: headfake.transformer.UpperCase

    gender:
      class: headfake.field.GenderField
      male_value: "M"
      female_value: "F"
      male_probability: 0.3

    last_name:
      class: headfake.field.LastNameField
      gender_field: gender
      transformers:
        - class: headfake.transformer.UpperCase

    dob:
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

## Analysis
This is a simple example of what HEADFAKE can do. It is straightforward to add additional fields to the template and to generate more/less rows of data. In the next tutorial we will take a closer look at the setup of the fields in the YAML file and modify them to create different data and formats.
