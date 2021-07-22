# Exclude fields from the output
The simplest way to do this is to add `hidden = true` to the field template.
For example if we don't want to include the gender field in the template below we would use:

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
      hidden: true

    - name: first_name
      class: headfake.field.FirstNameField
      gender_field: gender
```

The gender field is still created and used to determine the logic for the first name, but it is removed before the data is output.