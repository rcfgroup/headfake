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
    field_count = 0
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
        Create an instance of the HeadFake class with parameters loaded from a .yaml file

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
    def from_python(class_tree, **kwargs):
        """
        Create an instance of the HeadFake class from a pre-defined class tree

        Args:
            class_tree: the pre-defined class_tree
            **kwargs: additional arguments passed to HeadFake constructor

        Returns:
            a HeadFake instance

        Examples:
            ```python
            hf = HeadFake.from_python(
                headfake.Fieldset(
                    fields = {
                        "gender": headfake.field.GenderField(
                            male_value="M",
                            female_value="F",
                            male_probability=0.5
                        )
                ])
            )
            ```
        """

        return PyHeadFake(class_tree, **kwargs)


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
            locale: locale for generated data (e.g.

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

class PyHeadFake(HeadFake):
    def _create_fieldset(self, params):
        """
        Create the FieldSet from the parameters passed

        Args:
            params: parameters for the fieldset

        Returns:
            A FieldSet object
        """

        fieldset = params.get("fieldset")

        for field in fieldset.fields:
            field.init_from_fieldset(fieldset)

        return fieldset
