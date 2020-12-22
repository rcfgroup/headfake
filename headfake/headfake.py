"""
This file implements the HeadFake public API
"""

import random
import yaml
import numpy as np

from faker import Faker

from headfake.util import create_class_tree, locate_file

class HeadFake:
    """
    HeadFake class provide
    """
    def __init__(self, prarms, seed=None):
        """
        constructor - creates an instance of HeadFake object

        Args:
            prarms: parameters for generating data as a hierarchical dictionary
            seed: seed for initializing the pseudo-random generator
        """

        self.prarms = prarms

        if seed:
            random.seed(seed)
            np.random.seed(seed)
            Faker.seed(seed)

    @staticmethod
    def from_yaml(filename, **kwargs):
        """
        create HeadFake instance and load parameters from a .yaml file

        Args:
            filename: name of yaml template
            **kwargs: additional arguments passed to HeadFake constructor

        Returns:
            a HeadFake instance

        """
        path = locate_file(filename)
        return HeadFake(yaml.load(open(path), yaml.SafeLoader), **kwargs)

    def generate(self, num_rows):
        """
        generate random data based on the parameters specified in the constructor

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe
        """

        class_tree = create_class_tree(None, self.prarms)

        fieldset = class_tree.get("fieldset")
        for field in fieldset.fields.values():
            field.init_from_fieldset(fieldset)

        return fieldset.generate_data(num_rows)
