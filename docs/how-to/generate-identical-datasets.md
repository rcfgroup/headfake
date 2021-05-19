# Generate identical datasets

By default each time Headfake is run the generated data is very likely to be different (you can test this by running the same command multiple times).

However, sometimes you WILL want identical data to be generated every time (particularly in a test situation).

To do this you can provide a random seed which will be used through the system.

This can be done on the command line with the -s option. No matter how many times you run the command below you will get the same data generated.
```
headfake /path/to/tutorial1.yml -n100 -s1234
```

In Python this can be done through the static `set_seed` method of the HeadFake class:

```python
from headfake import HeadFake

HeadFake.set_seed(1234)
headfake = HeadFake.from_yaml("examples/patients.yaml")

data = headfake.generate(num_rows=100)
```