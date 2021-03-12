# Tutorial 2. Changing HEADFAKE configuration files

## Aims of tutorial
This tutorial will take a closer look at the YAML template and how to configure HEADFAKE fields.

## Adjust the proportion of male individuals
Open the `tutorial1.yml` you created in [Tutorial 1](/tutorials/tutorial1.md) in a text editor.

You will see that in essence it defines a Python class tree. The fieldset is the root element, this contains one or more fields.

If you looked at the `tutorial1.txt` file you would have seen that ~30% of the generated individuals are male. Let's change that likelihood
by adjusting the 'gender' field settings in `tutorial1.yml`.

Change `male_probability` to 0.5 and save the file as `tutorial2a.yml`:

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
headfake /path/to/tutorial2a.yml -o /path/to/tutorial2a.txt -n100
```

If you open `tutorial2.txt` you should see that the balance is closer to 50:50.

## Add a first name field

Into the 'fields' section of the YAML file copy the following and save as `tutorial2b.yml`

```yaml
first_name:
  class: headfake.field.FirstNameField
  gender_field: gender
```


Then re-run HEADFAKE:
```
headfake /path/to/tutorial2b.yml -o /path/to/tutorial2b.txt -n100
```

If you open the `tutorial2b.txt` file you should see that the new first_name field is generated according to the specified gender_field, dependent fields are a key part of the HEADFAKE setup and are described in more details in the discussion section.


We are using the gender field to determine whether the name generated is male or female.