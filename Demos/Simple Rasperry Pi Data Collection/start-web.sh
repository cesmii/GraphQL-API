#!/bin/bash
. venv/bin/activate
export FLASK_APP=web_datamonitor.py
echo "Serving Data to Clients..."
flask run --host=0.0.0.0 --port=5001


