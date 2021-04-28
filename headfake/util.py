"""
Utility methods used by other parts of Headfake
"""
import re
import errno
import os

from collections import OrderedDict
from importlib import import_module

from pathlib import Path
from importlib import resources

def create_package_class(package_name):
    """
    Utility method which loads and returns the class corresponding to the provided package name.
    :param package_name: Fully qualified package name.
    :return:
    """
    if not isinstance(package_name, str):
        return package_name

    package_bits = package_name.split(".")
    class_name = package_bits.pop()
    module = import_module(".".join(package_bits))
    if not hasattr(module, class_name):
        raise TypeError(
            "Could not create class '" + class_name + "' it does not exist in package '" + module.__name__ + "'")
    return getattr(module, class_name)


def create_class_tree(name, params):
    """Create recursive class tree given parameters.

    The name is only given if the original source had a key/value
    structure, otherwise None is supplied.

    Args:
        name:
            Name of the current class/object in the tree
        params:
            A dictionary or list of parameters used to build the class

    Returns:
        A class tree containing recursive classes, lists and dictionaries.

    """


    if isinstance(params, dict) and "class" in params:
        class_name = params["class"]
        del params["class"]
        sub_params = create_class_tree(name, params)

        cls = create_package_class(class_name)

        sub_params["name"] = name

        try:
            return cls(**sub_params)
        except TypeError as ex:
            handle_missing_keyword(ex)

            raise TypeError(
                "Problem creating '%s' %s. Original error:%s" %
                (name, cls, ex)) from ex

    new_params = OrderedDict()
    for key, value in params.items():
        if isinstance(value, dict):
            new_params[key] = create_class_tree(key, value)
        elif isinstance(value, list):
            block = []
            for item in value:
                block.append(create_class_tree(item.get("name", None), item))
            new_params[key] = block
        else:
            new_params[key] = value

    return new_params


def calculate_age(start_date: "datetime.date", end_date: "datetime.date"):
    """
    Calculate age in years when given start date and end date
    :param start_date: Date object for start
    :param end_date: Date object for end
    :return:
    """
    try:
        birthday = start_date.replace(year=end_date.year)

        # raised when birth date is February 29
        # and the current year is not a leap year
    except ValueError:
        birthday = start_date.replace(year=start_date.year,
                                      month=start_date.month + 1, day=1)

    if birthday > end_date:
        return end_date.year - start_date.year - 1

    return end_date.year - start_date.year


def locate_file(file):
    """
    Locates a file either from the given path or in the package resources

    :param file: The file to locate. It can either be an absolute or relative path in the
    filesystem or in the package resources
    :return: a PosixPath of the file if found. If the file is not found then an exception is raised
    """

    path = Path(file)

    if not path.is_file():
        # if file does not exist then check to see if it's in the package resources
        with resources.path("headfake", ".") as resource_root:
            path = resource_root / path

    if path.is_file():
        return path.absolute()

    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(file))


def handle_missing_keyword(ex):
    """
    Used to provides more informative error when a keyword is missing from parameters.
    :param ex: Original exception
    :return:
    """
    kwonly_error = re.search("required keyword-only argument[s]{0,1}: ('.+')$", str(ex))

    if kwonly_error:
        raise TypeError(
            "The following required parameter(s) were missing: %s" %
            kwonly_error.group(1))
