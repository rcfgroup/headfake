# Tutorial 3. Adding conditional fields

## Aims of tutorial
This tutorial will introduce a way of adding conditional logic for field value generation.

## Add title field based on gender and marital status
Conditional logic is handled using the IfElseField. To demonstrate how these fields work we will create some simple logic to generate the title of an individual, using the gender field and marital status field.

To keep it simpler at this stage we will not take into account other possible titles such as Ms. or Dr.

Open `tutorial2.yml`, add a new field as below and save as `tutorial3.yml`:

```yaml
title:
    class: headfake.field.IfElseField
    condition:
    	class: headfake.field.Condition
        field: gender
        operator: operator.equals
        value: M
    true_value:
        value: MR
    false_value:
        class: headfake.field.IfElseField
        condition:
            field: marital_status
            operator: equals
            value: M
        true_value: MRS
        false_value: MISS
```

Then try running it:
```
headfake /path/to/tutorial3.yml
```

You should now see that the 'title' field uses the 'gender' field as a lookup. If the value is 'M' it returns 'MR', if not then it uses another IfElse to look at the marital status. If this is 'M' then it returns 'MRS' and if not 'MISS'.

The IfElseField is quite flexible. If there is a string or number in the true_value/false_value option it will return that value, if it is a field definition it will return the generated value from the field.

## Enhancing conditional fields with probability
Let's improve this field by adding some level of chance to it and take into account other possible titles. Change the 'false_value: MISS' line to:

```yaml
false:
    class: OptionValueField
    probabilities:
        MISS: 0.7
        MS: 0.1
        DR: 0.1
        PROF: 0.1
```

And rerun headfake:
 ```
headfake /path/to/tutorial3.yml
```

You should now see that the output of title is now randomly either MISS, MS, DR or PROF based on the provided probabilities.

### Analysis
In this tutorial we showed how Headfake can be used to create fields dependent on the values of others. The ability to nest the if/else fields with constants or other field types can add a huge amount of variety to the data generation process.

This is the final tutorial. For more information about the field types in Headfake you can look at the API section of the documentation. Additionally, you can also [create and use your own pretty easily](/how-to/create-custom-field) if you find none of them meet your needs.

