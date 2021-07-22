# Combine field values

Operation fields enable you to generate data by combining values from two fields using a specified function.
For example, you could use an operation field to add, subtract or multiply generated values together. When operation fields are used it is best to use field lists rather than field maps
as this ensures the correct order of field generation.

In general, functions in Python's operator package are used, but you can actually specify any function (including your own) which accepts two input values and returns a single output value.

The examples below shows how this can be used to generate a hospital discharge date based on the admission date and a generated length of stay.

## Example 1 - 'length_of_stay' setup as a separate field and included in the data set:

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    - name: admission_date
      class: headfake.field.DateField
      min: "2020-01-01"
      max: "2020-12-31"
      distribution: scipy.stats.norm
      mean: "2020-06-01"
      sd: 30
      min_format: "%Y-%m-%d"
      max_format: "%Y-%m-%d"
      mean_format: "%Y-%m-%d"

    - name: length_of_stay
      class: headfake.field.NumberField
      min: 18
      max: 80
      distribution: scipy.stats.norm
      mean: 50
      sd: 15
      dp: 0

      transformers:
      - class: headfake.transformer.ConvertToDaysDelta

      final_transformers:
      - class: headfake.transformer.GetProperty
        prop_name: days

    - name: discharge_date
      class: headfake.field.OperationField
      operator: operator.add
      first_value:
        class: headfake.field.LookupField
        field: admission_date

      second_value:
        class: headfake.field.LookupField
        field: length_of_stay

      final_transformers:
      - class: headfake.transformer.FormatDateTime
        format: "%Y-%m-%d"

```

## Example 2 - length of stay embedded within the 'discharge_date' field so it is not available separately

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
    - name: admission_date
      class: headfake.field.DateField
      min: "2020-01-01"
      max: "2020-12-31"
      distribution: scipy.stats.norm
      mean: "2020-06-01"
      sd: 30
      min_format: "%Y-%m-%d"
      max_format: "%Y-%m-%d"
      mean_format: "%Y-%m-%d"

    - name: discharge_date
      class: headfake.field.OperationField
      operator: operator.add
      first_value:
        class: headfake.field.LookupField
        field: admission_date

      second_value:
        class: headfake.field.NumberField
        min: 18
        max: 80
        distribution: scipy.stats.norm
        mean: 50
        sd: 15
        dp: 0
        transformers:
        - class: headfake.transformer.ConvertToDaysDelta

      final_transformers:
      - class: headfake.transformer.FormatDateTime
        format: "%Y-%m-%d"
```

In both examples, the 'admission_date' field is a straightforward date field - it generates dates which follow a normal distribution.
The 'discharge_date' is more complex. It is an OperationField  which receives two values. In Example 1 the value is a look up in the separate 'length_of_stay' field while in Example 2 the value
is generated within the OperationField. In both cases, the length of stay is a random number which follows a normal distribution.

The same effect (ie. not including the length of stay field in the output could also have been achieved in Example 1 by adding a `hidden = true` property to the 'length_of_stay' field.

The length of stay is then converted into a Python timedelta object using a transformer and through the OperationField is added to the 'admission_date'.

The critical thing within the operation is that the value types (e.g. objects) need to be compatible with the operation function - this is why it was necessary to convert the numeric length of stay into a timedelta object as this can be added to a date object using `operator.add` (`operator.add(value1, value2)` is equivalent to `value1 + value2`).

Headfake comes with a number of conversion transformers which will change values into dates, numbers or strings and it is straightforward to [create custom transformers](create-custom-transformers.md) to do this.
