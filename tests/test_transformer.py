from headfake.transformer import UpperCase, IntermittentBlanks
from headfake.field import ConstantField, LastNameField, GenderField
from headfake.fieldset import Fieldset


def test_upper_case_transformer():
    constant = ConstantField(value="my_constant", transformers = [UpperCase()])
    assert constant.next_value({}) == "MY_CONSTANT"

def test_multiple_transformers_works_within_multiple_field_fieldset():
    fs = Fieldset(fields = {
        "last_name": LastNameField(gender_field="gender", transformers = [
        IntermittentBlanks(blank_probability=0.2, blank_value=None), UpperCase()
        ]),
        "gender":GenderField(male_value=1,female_value=0)}
    )
    fs.field_map["last_name"].next_value({"gender":"M"})
