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
IF "%~2" EQU "2" GOTO STEP2
IF "%~2" EQU "3" GOTO STEP3
SHIFT /2
GOTO MAIN


REM        -------------------------------------
REM  1 --> Prepare XReferences database syncing.
REM        -------------------------------------
:STEP1
FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
PUSHD %_parent%
python Dump_XReferences.py "%~1"
POPD
SET _parent=
SHIFT /2
GOTO MAIN


REM        ----------------------------
REM  2 --> Prepare NAS Syncing. Step 1.
REM        ----------------------------
:STEP2
PUSHD %_grabber%
python RippedTracks.py "%~1"
POPD
SHIFT /2
GOTO MAIN


:STEP3
PUSHD %TEMP%
ECHO "%~1">> cdgrabber.txt
POPD
SHIFT /2
GOTO MAIN
