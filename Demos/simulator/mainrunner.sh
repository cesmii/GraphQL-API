#!/bin/bash
python3 simulate.py tank functionchange test1 't+2' & 
python3 simulate.py tank functionchange test2 '2t+3' &
exit 0