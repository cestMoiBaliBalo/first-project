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
SET _jsonrippedcd=%TEMP%\rippinglog.json
SET _jsonrippedtracks=%TEMP%\digitalaudiodatabase.json


REM ===============
REM Main algorithm.
REM ===============


:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
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
SHIFT
GOTO MAIN
