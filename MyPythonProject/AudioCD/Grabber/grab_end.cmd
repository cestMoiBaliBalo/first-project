@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


@CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0


REM    ==================
REM B. Initializations 2.
REM    ==================
SET _mycp=
SET _cp=1252
SET _errorlevel=0
SET _jsontags=%TEMP%\tags.json


PUSHD %_myparent:~0,-1%


REM    ============
REM C. Main script.
REM    ============
PUSHD ..\..\..\Resources
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp (
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
    PUSHD ..
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET PATH=%_myparent%\MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    python insertAlbums.py "%_jsontags%"
    IF ERRORLEVEL 1 DEL "%_jsontags%" 2>NUL
    ENDLOCAL
    POPD
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
python RippedDiscs.py
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
@IF DEFINED _mycp CHCP %_mycp% > NUL
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
