# Tutorial 2. Changing Headfake configuration files

## Aims of tutorial
This tutorial will take a closer look at the YAML template including how changing the YAML file modifies the configuration, introduces some more advanced fields and look at how transformers can help post-process data.

## Adjust the proportion of male individuals
Open `tutorial1.yml` that you created in [Tutorial 1](/tutorials/tutorial1.md) in a text editor.
You will see that it consists of a hierarchy of Python classes, with the fieldset as the base element, which contains one or more fields. The properties of the fields are the arguments passed when the class is initialised, so by changing these values in the YAML file we change how the fields behave.

In the 'gender' field change the default `male_probability` from 0.3 to 0.5 and save the file as `tutorial2.yml`:

e.g.
```yaml
gender:
    class: headfake.field.GenderField
    male_value: "M"
    female_value: "F"
    male_probability: 0.5
```

Then re-run HEADFAKE:
```
headfake /path/to/tutorial2.yml -o /path/to/tutorial2a.txt -n100
```

If you open `tutorial2.txt` and compare with `tutorial1.txt` you should see that the balance in the former is about a third, whereas the latter is half.

## Add a first name field

You can also add additional fields by adding them into the 'fields' section of the YAML file.
You can try this by copying the following and pasting it into `tutorial2.yml` and saving:

```yaml
first_name:
  class: headfake.field.FirstNameField
  gender_field: gender
```

Then re-run HEADFAKE:
```
headfake /path/to/tutorial2.yml -o /path/to/tutorial2b.txt -n100
```

If you now open the `tutorial2b.txt` file you should see that the new first_name field is generated according to the specified gender_field.


## Generating patients who are deceased
Next you will add a field which can be very useful from a health perspective as it is a flag for deceased status.

Open `tutorial2.yml` and add a new field to the fieldset config as below:

e.g.
```yaml
deceased:
  class: headfake.field.DeceasedField
  dob_field: dob
  deceased_date_field: date_of_death
  age_field: age
  date_format: "%Y-%m-%d"
  # 1 in X risks taken from here. Used Male values. http://www.bandolier.org.uk/booth/Risk/dyingage.html
  risk_of_death:
	0-1: 177
	1-4: 4386
	5-14: 8333
	15-24: 1908
	25-34: 1215
	35-44: 663
	45-54: 279
	55-64: 112
	65-74: 42
	75-84: 15
	85-120: 6
```

Then re-run HEADFAKE:
```
headfake /path/to/tutorial2.yml -o /path/to/tutorial2c.txt -n100
```

If you now open `tutorial2c.txt` you will see that some individuals are now flagged as deceased, along with optional additional fields containing the date of death, and the age at which they died. The likelihood of death is calculated according to the risk of death supplied for the particular age ranges. Internally, patient aging is simulated and the likelihood of death determined accordingly.


## Changing generated data using a transformer

Transformers are special classes which act before or after data is generated. Here we are going to use two different ones to do two things: i) make last name uppercase and ii) create blank last name entries in our data.

Change the last_name in `tutorial2.yml` to add both transformers and re-run the generation:

```yaml
last_name:
      class: headfake.field.LastNameField
      gender_field: gender
      transformers:
        - class: headfake.transformer.IntermittentBlanks
          blank_probability: 0.2
          blank_value: NULL
        - class: headfake.transformer.UpperCase

```
headfake /path/to/tutorial2.yml -o /path/to/tutorial2d.txt -n100
```

As expected, ~20% of the values will now be NULL and those which are not will now be uppercase.


### Analysis
In this tutorial we showed how adaptable HEADFAKE can be for generating data by changing the YAML file. We were able to change the arguments to set up fields and add new fields. We also showed how transformers can be used to pre- and post-process generated field values.

In the final tutorial we will take a look at how conditional fields can be used to create a chain of fields dependent on each other.
