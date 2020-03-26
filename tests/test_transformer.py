from headfake.transformer import UpperCase
from headfake.field import ConstantField

def test_upper_case_transformer():
    constant = ConstantField(value="my_constant", transformers = [UpperCase()])
    assert constant.next_value({}) == "MY_CONSTANT"
