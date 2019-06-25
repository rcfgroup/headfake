# mock-data
Mock clinical data generation based on a code template
Python 3.5+ only supported.

Best thing to do is to create and activate a virtual environment although it will work on base Python.
```bash
python -m venv venv
source venv/bin/activate
```
Install requirements using pip:
```bash
pip install -r requirements.txt
```

Change settings in the mdconfig.py file to modify the output. The default is for generated data files to go into the
'output' directory.

Then run the script
```bash
python generate-mock-data.py
```