#!/usr/bin/env python
import os
import sys
from itertools import chain

from setuptools import setup
from setuptools.config import read_configuration

# Append cwd for pip 19
sys.path.append(os.path.abspath("."))

################################################################################
# Programmatically generate some extras combos.
################################################################################
extras = read_configuration("setup.cfg")["options"]["extras_require"]

# Dev is everything
extras["dev"] = list(chain(*extras.values()))

# All is everything but tests and docs
exclude_keys = ("tests", "docs", "dev")
ex_extras = dict(filter(lambda i: i[0] not in exclude_keys, extras.items()))
# Concatenate all the values together for 'all'
extras["all"] = list(chain.from_iterable(ex_extras.values()))

setup(
    extras_require=extras,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    package_data={'headfake': ['examples/*', 'examples/test_data/*']}
)
