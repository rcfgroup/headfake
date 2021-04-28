HEADFAKE is built around the concept of field sets which contain one or more fields.  Each field has a type (class) which determines what type of data is generated. The definition of fieldsets and their fields can be done through a YAML file or in Python code.

# Fieldsets from a YAML file
A YAML file can be used to describe the class tree which is created internally, and is then used to generate the data. For each item in the YAML file, the 'class' property defines the Python class used and all other properties are passed into the class constructor as parameters.

For example, for a dictionary-based template:

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

Or for a list-based template:

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
      - name: gender
        class: headfake.field.GenderField
        male_value: "M"
        female_value: "F"
        male_probability: 0.5
```

The `from_yaml` function is used:

```python
from headfake import HeadFake

hf = HeadFake.from_yaml("/path/to/template.yaml")
print(hf.fieldset)
```

The first template prints:
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

While the second gets turned into:

```python
headfake.Fieldset(
    fieldsets = [
        headfake.field.GenderField(
            name="gender",
            male_value="M",
            female_value="F",
            male_probability=0.5
        )
])
```

The advantage of the list-based approach is that the order of fields is always retained, whereas it may not with a dictionary-based template - as the YAML specification does not retain the order of values in the file.

# Fieldset in Python code
If preferred, the fieldset definition can be written in Python code directly. This should be fed to the 'from_python' method:

```python
hf = HeadFake.from_python(headfake.Fieldset(
    fieldsets = [
        headfake.field.GenderField(
            name="gender",
            male_value="M",
            female_value="F",
            male_probability=0.5
        )
]))
```

This will initialise the fields appropriately.

## Generate data
Once the HeadFake object has been obtained, the key method is generate_data which processes each field to create a pandas DataFrame containing the specified number of rows of generated data.
