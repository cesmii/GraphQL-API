@echo off
echo "Starting One Tank System..."
del config.py
copy config-onetank.py config.py /y
python3 simulate.py tank normalflow
