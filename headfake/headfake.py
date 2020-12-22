"""
This file implements the HeadFake public API
"""
import random

from faker import Faker

from headfake.util import class_tree_from_yaml_file, locate_file

class HeadFake:
    """
    HeadFake class provide
    """
    def __init__(self, template, seed=None):
        self.template = template
        if seed:
            random.seed(seed)
            Faker.seed(seed)

    def generate(self, num_rows):
        template = locate_file(self.template)

        class_tree = class_tree_from_yaml_file(template)

        fieldset = class_tree.get("fieldset")
        return fieldset.generate_data(num_rows)
