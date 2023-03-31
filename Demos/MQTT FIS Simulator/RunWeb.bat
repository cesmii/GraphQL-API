@ECHO OFF
IF EXIST ".\web\config.js" GOTO EXISTS
ECHO.
ECHO No config.js exists. 
ECHO Copy web\config-example.js to web\config.js and enter the SMIP Credentials.
ECHO.
GOTO END
:EXISTS
cd web
python -m http.server
:END