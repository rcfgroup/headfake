HEADFAKE is built around the concept of field sets which contain one or more fields.  Each field has a type (class) which determines what type of data is generated. The definition of fieldsets and their fields is done through a YAML file.

The YAML file describes the class tree which is created internally and is then used to generate the data. For each item in the class tree, the 'class' property defines the Python class uses and all other properties are passed into the class constructor as paramers.

For example

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    gender:
        class: headfake.field.GenderField
        male_value: "M"
        female_value: "F"
        male_probability: 0.5
```

Gets turned into
```python
headfake.Fieldset(
    fieldsets = {
        "gender": headfake.field.GenderField(
            male_value="M",
            female_value="F",
            male_probability=0.5
        )
})

```

The key method in the fieldset is generate_data which processes each field to create a data frame
containing the specified number of rows of generated data.
