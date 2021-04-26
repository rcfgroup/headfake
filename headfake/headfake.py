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
    Provides the core logic as a class which has an input a parameter dictions.
    Includes support for populating the HeadFake class from a YAML file.
    """

    locale = "en_GB"

    def __init__(self, params, seed=None):
        """
        Creates an instance of the HeadFake object

        Args:
            params: parameters for generating data as a hierarchical dictionary
            seed: seed for initializing the pseudo-random generator
        """
        self.set_seed(seed)
        self.fieldset = self._create_fieldset(params)


    @staticmethod
    def from_yaml(filename, **kwargs):
        """
        Create and instance of the HeadFake instance with parameters loaded from a .yaml file

        Args:
            filename: name of yaml template
            **kwargs: additional arguments passed to HeadFake constructor

        Returns:
            a HeadFake instance

        """
        path = locate_file(filename)
        with open(path) as file:
            params = yaml.safe_load(file)
        return HeadFake(params, **kwargs)

    @staticmethod
    def set_seed(seed):
        """
        Set the seed for initializing random number generator

        Args:
            seed: seed for initializing random number generator

        Returns:
            None

        """

        random.seed(seed)
        np.random.seed(seed)
        Faker.seed(seed)

    @classmethod
    def set_locale(cls, locale):
        """
        Set the locale for random value generation

        Args:
            seed: seed for initializing random number generator

        Returns:
            None

        """
        cls.locale = locale


    def _create_fieldset(self, params):
        """
        Create the FieldSet from the parameters passed

        Args:
            params: parameters for the fieldset

        Returns:
            A FieldSet object
        """

        class_tree = create_class_tree(None, params)

        fieldset = class_tree.get("fieldset")

        for field in fieldset.fields:
            field.init_from_fieldset(fieldset)

        return fieldset


    def generate(self, num_rows=1):
        """
        Generate fake data based on the parameters specified in the constructor

        Args:
            num_rows: number of rows to generate

        Returns:
            a pandas dataframe
        """

        return self.fieldset.generate_data(num_rows)
