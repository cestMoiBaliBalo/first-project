@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _mycp=
SET _cp=1252
SET _errorlevel=0
SET _grabber=%_PYTHONPROJECT%\AudioCD\Grabber
SET _jsontags=%TEMP%\tags.json
SET _jsonxreferences=%TEMP%\xreferences.json
SET _txtfiles=%_RESOURCES%\rippedtracks.txt


REM ============
REM Main script.
REM ============
SET _chcp=
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)


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
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38;!PATH!
    FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
    PUSHD !_parent!
    python Insert_Albums.py "%_jsontags%"
    POPD
    ENDLOCAL
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
SETLOCAL
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
PUSHD %_grabber%
python RippedDiscs.py
POPD
ENDLOCAL
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
    SET _cp=
    SET _me=
    SET _chcp=
    SET _mycp=
    SET _path=
    SET _grabber=
    SET _jsontags=
    SET _myparent=
    SET _txtfiles=
    SET _errorlevel=
    SET _jsonxreferences=
    IF DEFINED _mycp CHCP %_mycp% > NUL
    ENDLOCAL
    EXIT /B %_errorlevel%
)
