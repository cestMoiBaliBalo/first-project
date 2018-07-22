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
SET _errorlevel=0
SET _jsontags=%TEMP%\tags.json


REM ============
REM Main script.
REM ============


:MAIN
IF "%~1" EQU "" EXIT /B %_errorlevel%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
SHIFT
GOTO MAIN

REM        -----------------------
REM  1 --> Digital audio database.
REM        -----------------------
:STEP1
IF EXIST "%_jsontags%" (
    python %_PYTHONPROJECT%\AudioCD\Views\Albums.py "%_jsontags%"
    DEL "%_jsontags%" 2>NUL
)
SHIFT
GOTO MAIN


REM        -------------------------
REM  2 --> Update Ripping log views.
REM        -------------------------
:STEP2
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tables
REM python RippedDiscsView1.py
REM python RippedDiscsView2.py 1
REM python RippedDiscsView3.py
REM python AlbumsView.py
REM POPD
SHIFT
GOTO MAIN
