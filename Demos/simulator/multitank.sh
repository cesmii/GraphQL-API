#!/bin/bash
echo "Starting Multiple Tank System..."
rm config.py
cp config-multitank.py config.py
python3 simulate.py tank normalflow
