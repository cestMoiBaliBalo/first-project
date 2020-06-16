@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
PUSHD %_PYTHONPROJECT%\AudioCD


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0


REM    ==================
REM B. Initializations 1.
REM    ==================
SET _mycp=
SET _cp=1252
SET _errorlevel=0
SET _jsontags=%TEMP%\tags.json
SET _jsonxreferences=%TEMP%\xreferences.json


REM    ============
REM C. Main script.
REM    ============
PUSHD %_RESOURCES%
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)
POPD


:MAIN
IF "%~1" EQU "" GOTO THE_END
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
SHIFT
GOTO MAIN


REM        -----------------------------------------------
REM  1 --> Append ripped tracks to digital audio database.
REM        -----------------------------------------------
:STEP1
IF EXIST "%_jsontags%" (
    python Insert_Albums.py "%_jsontags%"
    DEL "%_jsontags%" 2>NUL
)
SHIFT
GOTO MAIN


REM        ----------
REM  2 --> Available.
REM        ----------
:STEP2
SHIFT
GOTO MAIN


REM        ------------------------------
REM  3 --> Update ripped discs dashboard.
REM        ------------------------------
:STEP3
PUSHD Grabber
python RippedDiscs.py
POPD
SHIFT
GOTO MAIN


REM        ----------
REM  4 --> Available.
REM        ----------
:STEP4
SHIFT
GOTO MAIN


REM        --------------
REM  5 --> Miscellaneous.
REM        --------------
:STEP5
PUSHD %TEMP%
DEL sequences.json 2> NUL
POPD
SHIFT
GOTO MAIN


REM        ------------
REM  6 --> Exit script.
REM        ------------
:THE_END
(
    IF DEFINED _mycp CHCP %_mycp% > NUL
    POPD
    ENDLOCAL
    CLS
    EXIT /B %_errorlevel%
)
