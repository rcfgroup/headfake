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

If you open the `tutorial2b.txt` file you should see that the new first_name field is generated according to the specified gender_field.

## Add middle name field based on gender
Name fields are an example of pre-defined if/else fields which are a key part of HEADFAKE. The value generated in these fields is dependent on values in other fields.

To demonstrate how to use this approach we are going to create a simple logic field containing a title (not taking into account other possible titles such as Ms. or Dr.) of an individual using the gender field and marital status field.


```yaml
title:
    class: headfake.field.IfElseField
    condition:
        field: gender
        operator: equals
        value: M
    true:
        class: headfake.field.ConstantField
        value: MR
    false:
        class: headfake.field.IfElseField
        condition:
            field: marital_status
            operator: equals
            value: M
        true: MRS
        false: MISS
```

This contains a nested IfElse which uses the 'gender' field as a lookup. If the value is 'M' it returns 'MR', if not then it uses another IfElse to look at the marital status. If it is 'M' then it returns 'MRS' and if not 'MISS'.

The IfElseField is quite flexible. If there is a string in the true/false option it will return the string, if a field it will return the results from the field.

## Enhancing title with probability
Lets improve this field by adding some probability to it. Change the 'false: MISS' line to:

```
false:
    class: OptionValueField
    probabilities:
        MISS: 0.7
        MS: 0.1
        DR: 0.1
        PROF: 0.1
```

And rerun headfake. If you look at the output file you will see that it is now randomly either MISS, MS, DR or PROF based on the provided probabilities.

### Analysis
In this tutorial we showed how adaptable HEADFAKE can be for generating data, including the ability to create fields dependent on the values of others. The ability to nest the if/else fields can add a huge amount of variety to the data generation process.

title:
    class: headfake.field.CaseWhenField
    field: gender
    - case:
      operator: equals
      value: M
      result:
        class: headfake.field.ConstantField
        value: MR
    else:
        class: headfake.field.CaseWhenField
        field: marital_status
        - case:
          operator: equals
          value: M
          result: MRS

        - case:
          operator: in
          value: [C,S,P]
          result:
             class: OptionValueField
             probabilities:
               MISS: 0.7
               MS: 0.1
               DR: 0.1
               PROF: 0.1

