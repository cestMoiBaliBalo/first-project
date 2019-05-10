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
SET _cp=1252
SET _errorlevel=0
SET _grabber=%_PYTHONPROJECT%\AudioCD\Grabber


REM ============
REM Main script.
REM ============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


:MAIN
IF "%~2" EQU "" EXIT /B %_errorlevel%
IF "%~2" EQU "1" GOTO STEP1
IF "%~2" EQU "2" GOTO STEP2
SHIFT /2
GOTO MAIN


REM        -----------------------
REM  1 --> Digital audio database.
REM        -----------------------
:STEP1
PUSHD %_grabber%
python XReferences.py "%~1"
POPD
SHIFT
GOTO MAIN


REM        ---------------------
REM  2 --> XReferences database.
REM        ---------------------
:STEP2
PUSHD %_grabber%
python RippedTracks.py "%~1"
POPD
SHIFT
GOTO MAIN
