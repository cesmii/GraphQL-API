@ECHO OFF
IF EXIST ".\config.py" GOTO EXISTS
ECHO.
ECHO No config.py exists. 
ECHO Copy config-example.py to config.py and enter the SMIP Credentials.
ECHO.
GOTO END
:EXISTS
python .\sim.py
:END