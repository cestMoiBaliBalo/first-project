@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _audiocd=%_PYTHONPROJECT%\AudioCD
SET _cp=1252
SET _errorlevel=0
SET _jsontags=%TEMP%\tags.json
SET _jsonxreferences=%TEMP%\xreferences.json


REM ============
REM Main script.
REM ============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


:MAIN
IF "%~1" EQU "" EXIT /B %_errorlevel%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
SHIFT
GOTO MAIN

REM        -----------------------
REM  1 --> Digital audio database.
REM        -----------------------
:STEP1
IF EXIST "%_jsontags%" (
    PUSHD %_audiocd%
    python Albums.py "%_jsontags%"
    POPD
    DEL "%_jsontags%" 2>NUL
)
SHIFT
GOTO MAIN

REM        ---------------------
REM  2 --> XReferences database.
REM        ---------------------
:STEP2
IF EXIST "%_jsonxreferences%" (
    PUSHD %_audiocd%
    python XReferences.py "%_jsonxreferences%"
    POPD
    DEL "%_jsonxreferences%" 2>NUL
)
SHIFT
GOTO MAIN

REM        -----------------------
REM  3 --> Ripped discs dashboard.
REM        -----------------------
:STEP3
PUSHD %_audiocd%\Grabber
python RippedDiscs.py
POPD
SHIFT
GOTO MAIN
