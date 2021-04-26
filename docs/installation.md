# Installation

## From pypi
This package requires Python 3.6 or above. We recommend that you install it in a virtual environment using the standard Python Package Index (pypi). Here we have installed it in the myproject directory:

```bash
mkdir /path/to/myproject
cd /path/to/myproject
python3 -mvenv venv
source venv/bin/activate
pip install headfake
```

# From github
If you wish to use the latest version of the tool it can be installed from github:

```bash
pip install git+ssh://git@github.com/rcfgroup/headfake.git@develop
```

# For development

If you're developing this package, you can install it using pip as shown below:

```bash
pip install -e ".[tests]"
```

# With documentation
HEADFAKE uses [Portray](https://timothycrosley.github.io/portray/) to build documentation with embedded API docs. You can install the dependencies using pip as shown below:
```bash
pip install -e ".[docs]"
```

Then to build the docs it should be as simple as running:
```bash
portray as_html
```

Or to view them:
```bash
portray in_browser
```
