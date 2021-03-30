import errno
import os
import yaml

from collections import OrderedDict
from importlib import import_module
from inspect import signature
from pathlib import Path


def create_package_class(package_name):
    package_bits = package_name.split(".")
    class_name = package_bits.pop()
    module = import_module(".".join(package_bits))
    if not hasattr(module, class_name):
        raise TypeError(
            "Could not create class '" + class_name + "' it does not exist in package '" + module.__name__ + "'")
    return getattr(module, class_name)


import re

def create_class_tree(name, params, data=None):
    """
    Create class tree given parameters. The name is only given if the original source had a key/value structure,
    otherwise None is supplied.
    :param name:
    :param params:
    :param data:
    :return:
    """
    if data is None:
        data = {}

    if isinstance(params, dict) and "class" in params:
        class_name = params["class"]
        del (params["class"])
        sub_params = create_class_tree(name, params, data)

        cls = create_package_class(class_name)
        sig = signature(cls)

        # if "name" in sig.parameters:
        sub_params["name"] = name

        try:
            return cls(**sub_params)
        except TypeError as ex:
            handle_missing_keyword(ex)

            raise TypeError("Problem creating '%s' %s. Original error:%s" % (name, cls.__name__, ex))

    new_params = OrderedDict()
    for key, value in params.items():
        if isinstance(value, dict):
            new_params[key] = create_class_tree(key, value, data)
        elif isinstance(value, list):
            block = []
            for item in value:
                block.append(create_class_tree(item.get("name",None), item, data))
            new_params[key] = block
        else:
            new_params[key] = value

    return new_params


def class_tree_from_yaml_file(yaml_filename):
    """
    Builds class tree recursively using YAML file as a template. The current algorithm may not be the most performant.
    :param yaml_filename:
    :return:
    """
    with open(yaml_filename, "r") as yaml_file:
        data = yaml.load(yaml_file, yaml.SafeLoader)

    class_tree = create_class_tree(None, data)

    fset = class_tree.get("fieldset")
    for fname, field in fset.fields.items():
        field.init_from_fieldset(fset)

    return class_tree


def retrieve_from_data(placeholder, data):
    if len(placeholder) == 1:
        return data[placeholder[0]]

    return retrieve_from_data(placeholder[1:], data[placeholder[0]])


def calculate_age(start_date: "datetime.date", end_date: "datetime.date"):
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


def locate_file(file):
    """
    locate a file either from the given path or in the package resources

    :param file: The file to locate. It can either be an absolute or relative path in the
    filesystem or in the package resources
    :return: a PosixPath of the file if found. If the file is not found then an exception is raised
    """

    try:
        from importlib import resources
    except ImportError:
        import importlib_resources as resources

    path = Path(file)

    if not path.is_file():
        # if file does not exist then check to see if it's in the package resources
        with resources.path("headfake", ".") as resource_root:
            path = resource_root / path

    if path.is_file():
        return path.absolute()

    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(file))

def handle_missing_keyword(ex):
    kwonly_error = re.search("required keyword-only argument[s]{0,1}: ('.+')$", str(ex))

    if kwonly_error:
        raise TypeError("The following required parameter(s) were missing: %s" % kwonly_error.group(1))