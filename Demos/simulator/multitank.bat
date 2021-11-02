@echo off
echo "Starting Multiple Tank System..."
del config.py
copy config-multitank.py config.py /y
python3 simulate.py tank normalflow
