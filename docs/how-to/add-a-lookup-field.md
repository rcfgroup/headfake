## Lookup values in another file
Headfake allows you to populate a field with a randomly selected field value from another file, and use this to lookup
information.

The YAML for this is as follows:

```yaml
fieldset:
  class: headfake.Fieldset
  fields:
  	ext_pat_id:
      class: headfake.MapFileField
      key_field: <field_in_other_file>
      mapping_file: <other_file>

    last_name:
      class: headfake.field.LookupMapFileField
      lookup_value_field: <field_to_lookup>
      map_file_field: ext_pat_id
```

The other file will need to be present in order for this to work. Currently, Headfake does not support multi-file
generation.
