# Tutorial 3. Adding conditional fields

## Aims of tutorial
This tutorial will introduce the IfElseField which allows you to define conditional logic for field value generation.

## Add title field based on gender and marital status
To demonstrate how IfElse fields work we are going to create a simple logic field containing the title of an individual, using the gender field and marital status field. To keep this simple at this stage we will not take into account other possible titles such as Ms. or Dr.

Open `tutorial2.yml` and add a new field as below:

```yaml
title:
    class: headfake.field.IfElseField
    condition:
    	class: headfake.field.Condition
        field: gender
        operator: operator.equals
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
        true_value: MRS
        false_value: MISS
```

This acts as a nested conditional using the 'gender' field as a lookup. If the value is 'M' it returns 'MR', if not then it uses another IfElse to look at the marital status. If this is 'M' then it returns 'MRS' and if not 'MISS'.

The IfElseField is quite flexible. If there is a string in the true/false option it will return the string, if a field it will return the results from the field.

## Enhancing conditional fields with probability
Lets improve this field by adding some level of chance to it. Change the 'false_value: MISS' line to:

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
In this tutorial we showed how adaptable Headfake can be for generating data, including the ability to create fields dependent on the values of others. The ability to nest the if/else fields can add a huge amount of variety to the data generation process.

This is the final tutorial. For more information about the field types in Headfake you can look at the API section of the documentation. Additionally, you can also [create and use your own pretty easily](/how-to/create-custom-field) if you find none of them meet your needs.

