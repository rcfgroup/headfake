# Create custom transformers

A transformer a special class which acts after the data is generated from a field. The points at which these are run is depends on whether they are passed into the field in the 'transformers' list or in the 'final_transformers' list.
The former runs as soon as a value is generated in the field, the latter runs once all data has been generated in the row, so are more suited to formatting data ready for output.

Custom transformers can be created by extending the Transformer class in headfake.transformer. If you want to allow parameters to be passed to your transformer Headfake they should be setup using the approaches documented in the [attrs](https://www.attrs.org) package, which provides a simpler way of initialising and handling class properties.


## An example transformer
Below is a simple transformer which splits a string by a 'separator' to create a list and returns the piece from this list specified by 'index'. Each of these parameters can be specified by the user.

An example of how this could be used would be generating a partial UK postcode - you want to create a column containing just the first part of it (e.g. the AB1 from AB1 2CD).

```python

@attr.s(kw_only=True)
from headfake.transformer import Transformer

class SplitPiece(Transformer):
    separator = attr.ib() #string to separator on
	index = attr.ib() #index of separated string to return

    def transform(self, field, row, value):
    	pieces = value.split(self.separator)

		if len(pieces)<self.index:
			return ""

    	return pieces[self.index]

..

postcode_field = PostcodeField(transformers=[
	SplitPiece(separator=" ",index=0)
])
```

## Using custom transformers in YAML templates

This is as simple as entering the classname in the 'class' property in the YAML file along with the additional parameters. For example to use the SplitPieceTransformer in a field:

```yaml
...
postcode:
	class: headfake.field.PostcodeField
	transformers:
		- class: mypackage.SplitPieceTransformer
		  separator: " "
		  index: 0
...
```
