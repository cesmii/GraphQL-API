## CESMII OPC UA Machine Simulator

### Setup
Dependenices to install via pip:
```
pip install opcua
```
Documentation on this Python OPC UA server is located here: https://python-opcua.readthedocs.io/en/latest/

Run with: `python3 opcua-machinesim.py`

### Configuration
Command line arguments not currently implemented, most configuration can be done in the lines after the imports.

The most important part is the data file. It should be a CSV, with a header row that includes labels. At least one column should be named `Timestamp` -- its value will be ignored and substituted with the current time. All other column values must be `float` for now.

See the included `FestoData.csv` for examples. This file is used by default.
