# Tutorial 3. Adding more advanced elements

## Aims of tutorial
This tutorial will add some more advanced elements to the YAML template and look at how transformers can help post-process data.

## Generating patients who are deceased
Open `tutorial2b.yml` you created in [Tutorial 2](/tutorials/tutorial2.md) in a text editor.

Add a deceased flag to the fieldset as below and save the file as `tutorial3a.yml`:

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
headfake /path/to/tutorial3a.yml -o /path/to/tutorial3a.txt -n100
```

If you now open `tutorial3a.txt` you should see that some individuals are now flagged as deceased, along with additional fields containing the date of death, and the age at which they died (these are optional). The likelihood of death is calculated according to the risk of death for particular age ranges. Internally, patient aging is simulated and the likelihood of death determined accordingly.

This powerful field could be combined with conditional IfElse fields to support different risk profiles.


## Simulate blanks using a transformer

Transformers are special classes which act before or after data is generated. Here we are going to use them to create blank last name entries in our data. But there are also transformers which will truncate data, change its case or create zero padded values, and it is easy to create your own transformer classes to modify the generate data.
Modify the last_name in `tutorial3a.yml` to add a transformer and re-run the generation:

```yaml
last_name:
      class: headfake.field.LastNameField
      gender_field: gender
      transformers:
        - class: headfake.transformer.IntermittentBlanks
          blank_probability: 0.2
          blank_value: NULL

As expected, ~20% of the values will now be NULL.


## Lookup values in another file
Headfake allows you to populate a field with a randomly selected field value from another file, and use this to lookup information.

To show how this works, create a new YAML file called tutorial3b.yml and paste in the following:
```yaml
fieldset:
  class: headfake.Fieldset
  fields:
  	ext_pat_id:
      class: headfake.MapFileField
      key_field: main_pat_id
      mapping_file: tutorial3a.txt

    last_name:
      class: headfake.field.LookupMapFileField
      lookup_value_field: last_name
      map_file_field: ext_pat_id
```

Then re-run HEADFAKE:
```
headfake /path/to/tutorial3b.yml -o /path/to/tutorial3b.txt -n100
```

If you examine the output file, you will see randomly selected main_pat_id values, from the `tutorial3a.txt` file and the last name that was associated with that ID.

### Analysis
In this tutorial we showed how adaptable HEADFAKE can be for generating data, including the ability to create fields dependent on the values of others. The ability to nest the if/else fields can add a huge amount of variety to the data generation process.
