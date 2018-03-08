@ECHO off
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _errorlevel=0
SET _jsonrippedcd=%TEMP%\rippinglog.json
SET _jsonrippedtracks=%TEMP%\digitalaudiodatabase.json


REM ===============
REM Main algorithm.
REM ===============


:MAIN
IF "%~1" EQU "" EXIT /B %_errorlevel%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
SHIFT
GOTO MAIN


REM        ------------
REM  1 --> Ripping log.
REM        ------------
:STEP1
IF EXIST "%_jsonrippedcd%" (
    python %_PYTHONPROJECT%\AudioCD\RippedCD.py "%_jsonrippedcd%"
    SET _inserted=!ERRORLEVEL!
    SET /A "_errorlevel+=!_inserted!"
    FOR /F "usebackq" %%I IN (`DATE /T`) DO SET _date=%%I
    FOR /F "usebackq" %%I IN (`TIME /T`) DO SET _time=%%I
    ECHO !_date! - !_time! - !_inserted! >> %_COMPUTING%\Log\ripper.txt
    DEL "%_jsonrippedcd%"
)
SHIFT
GOTO MAIN


REM        -----------------------
REM  2 --> Digital audio database.
REM        -----------------------
:STEP2
IF EXIST "%_jsonrippedtracks%" (
    python %_PYTHONPROJECT%\AudioCD\RippedTracks.py "%_jsonrippedtracks%"
    SET _inserted=!ERRORLEVEL!
    SET /A "_errorlevel+=!_inserted!"
    FOR /F "usebackq" %%I IN (`DATE /T`) DO SET _date=%%I
    FOR /F "usebackq" %%I IN (`TIME /T`) DO SET _time=%%I
    ECHO !_date! - !_time! - !_inserted! >> %_COMPUTING%\Log\ripper.txt
    DEL "%_jsonrippedtracks%"
)
SHIFT
GOTO MAIN


REM        -------------------------
REM  3 --> Update Ripping log views.
REM        -------------------------
:STEP3
python %_PYTHONPROJECT%\AudioCD\RippedCD`View1.py
python %_PYTHONPROJECT%\AudioCD\RippedCD`View2.py
python %_PYTHONPROJECT%\AudioCD\RippedCD`View3.py
python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
SHIFT
GOTO MAIN
