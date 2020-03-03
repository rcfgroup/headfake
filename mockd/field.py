from random import random


class IncrementalField:
    def __init__(self, suffix, length, start_at):
        self.suffix = suffix
        self.length = length
        self.start_at = start_at
        self.current_no = self.start_at

    def next_value(self):
        curr_no  = str(self.current_no).zfill(self.length)
        self.current_no+=1
        return self.suffix + curr_no

class GenderField:
    def __init__(self, male_value, female_value, male_probability=0.5):
        self.male_value = male_value
        self.female_value = female_value
        self.male_probability = male_probability

    def next_value(self):
        return self.male_value if random() < self.male_probability else self.female_value