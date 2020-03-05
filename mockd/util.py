import re
from collections import OrderedDict
from importlib import import_module
from inspect import signature
import yaml

def create_package_class(package_name):
    package_bits = package_name.split(".")
    class_name = package_bits.pop()
    module = import_module(".".join(package_bits))
    if not hasattr(module,class_name):
        raise TypeError("Could not create class '" + class_name + "' it does not exist in package '" + module.__name__ + "'")
    return getattr(module, class_name)

def create_class_tree(name, params, data={}):
    if isinstance(params, dict) and "class" in params:
        class_name = params["class"]
        del(params["class"])
        sub_params = create_class_tree(name,params,data)

        cls = create_package_class(class_name)
        sig = signature(cls)

        #if "name" in sig.parameters:
        sub_params["name"] = name

        try:
            return cls(**sub_params)
        except TypeError as ex:
           raise TypeError("Problem creating '%s' %s. Original error:%s" % (name, cls.__name__,ex))


    new_params = OrderedDict()
    for k,v in params.items():
        if isinstance(v, dict):
            new_params[k]=create_class_tree(k,v, data)
        elif isinstance(v, list):
            block = []
            for item in v:
                block.append(create_class_tree(None, item, data))
            new_params[k] = block
        else:
            match = re.match("\<(.+)\>",k)

            if match:
                new_params[k]=retrieve_from_data(match.group(0), data)
            else:
                new_params[k]=v

    return new_params

def config_from_yaml_file(yaml_filename):
    with open(yaml_filename,"r") as yaml_file:
        data = yaml.load(yaml_file,  yaml.SafeLoader)

    return config_from_data(data)

def config_from_data(data):
    return create_class_tree(None, data)

def retrieve_from_data(placeholder, data):
    if len(placeholder)==1:
        return data[placeholder[0]]

    return retrieve_from_data(placeholder[1:],data[placeholder[0]])

class Config:
    def __init__(self, **kwargs):
        [setattr(self,k,v) for k,v in kwargs.items()]

def calculate_age(start_date:"datetime.date", end_date:"datetime.date"):
    try:
        birthday = start_date.replace(year=end_date.year)

        # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError:
        birthday = start_date.replace(year=start_date.year,
                                      month=start_date.month + 1, day=1)

    if birthday > end_date:
        return end_date.year - start_date.year - 1
    else:
        return end_date.year - start_date.year