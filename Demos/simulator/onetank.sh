#!/bin/bash
echo "Starting One Tank System..."
rm config.py
cp config-onetank.py config.py
#python3 simulate.py tank fillthendrain
python3 simulate.py tank normalflow
