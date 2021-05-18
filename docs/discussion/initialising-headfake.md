# Initialising Headfake

Headfake is based on field sets which contain one or more fields.  Each field has a type (class) which determines what type of data is generated OR if a generated value is a constant it can be provided as a string, integer etc.

The definition of fieldsets and their fields can be done through a YAML file or in Python code.

# Fieldsets from a YAML file
Headfake currently supports the use of a YAML file to describe the layout of the fields. This is then used to generate the data. For each item in the YAML file, a 'class' property defines the Python class or type used and all other properties are passed into the class constructor as parameters. If there is not 'class' property, the values are passed in their raw form (e.g. as a string or number).

Headfake supports defining fields as a list:

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
      - name: gender
        class: GenderField
        male_value: "M"
        female_value: "F"
        male_probability: 0.5
```

Or as a dictionary:
```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    gender:
        class: GenderField
        male_value: "M"
        female_value: "F"
        male_probability: 0.5
```

!!! note
	Both approaches return valid HeadFake fieldsets, but YAML does not support ordered dictionaries. So if the order of
	the generated fields is important you should use the list-based approach. If not then either can be used.

Data can then either be generated using the `headfake` command (see [usage](usage)) or in Python
using the `from_yaml` function:

```python
from headfake import HeadFake

hf = HeadFake.from_yaml("/path/to/template.yaml")
print(hf.generate(100))
..
```

The advantage of the list-based approach is that the order of fields is always retained, whereas it may not with a dictionary-based template - as the YAML specification does not retain the order of values in the file.

# Fieldset in Python code
If preferred, the fieldset definition can be written in Python code directly. This can either be done as a series of
data structures:

```python
from headfake import field, HeadFake, fieldset

# as a dictionary of fields:

hf = HeadFake({
	"class":"headfake.fieldset.Fieldset",
	"fields":{
		"gender":{"class":"GenderField","male_value":"M","female_value":"F","male_probability":0.5}
	}
})

# as a list of fields:
hf = HeadFake({
	"class":"headfake.fieldset.Fieldset",
	"fields":[
		{"name":"gender","class":"GenderField","male_value":"M","female_value":"F","male_probability":0.5}
	]
})

# as Python classes:

hf = HeadFake.from_python(fieldset.Fieldset(
    fieldsets = [
        headfake.field.GenderField(
            name="gender",
            male_value="M",
            female_value="F",
            male_probability=0.5
        )
]))
```

## Generate data
Once the HeadFake object has been obtained, you can use the `generate_data` method to return a pandas DataFrame containing the specified number of rows of generated data.

```python
# generate 100 rows of data
df = hf.generate_data(100)
```