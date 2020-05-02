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
IF "%~2" EQU "" GOTO THE_END
IF "%~2" EQU "1" GOTO STEP1
IF "%~2" EQU "2" GOTO STEP2
IF "%~2" EQU "3" GOTO STEP3
SHIFT /2
GOTO MAIN


REM        ----------
REM  1 --> Available.
REM        ----------
:STEP1
SHIFT /2 
GOTO MAIN


REM        ----------------------------
REM  2 --> Prepare NAS Syncing. Step 1.
REM        ----------------------------
:STEP2
SETLOCAL
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
PUSHD %_grabber%
python RippedTracks.py "%~1"
POPD
ENDLOCAL
SHIFT /2
GOTO MAIN


REM        ----------
REM  3 --> Available.
REM        ----------
:STEP3
SHIFT /2
GOTO MAIN


REM        ------------
REM  4 --> Exit script.
REM        ------------
:THE_END
(
    SET _cp=
    SET _me=
    SET _chcp=
    SET _mycp=
    SET _grabber=
    SET _myparent=
    SET _errorlevel=
    IF DEFINED _mycp CHCP %_mycp% > NUL
    ENDLOCAL
    EXIT /B %_errorlevel%
)
