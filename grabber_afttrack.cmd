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


REM        -------------------------------------
REM  1 --> Prepare XReferences database syncing.
REM        -------------------------------------
:STEP1
REM FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
REM PUSHD %_parent%
REM python Dump_XReferences.py "%~1"
REM POPD
REM SET _parent=
SHIFT /2 
GOTO MAIN


REM        ----------------------------
REM  2 --> Prepare NAS Syncing. Step 1.
REM        ----------------------------
:STEP2
REM PUSHD %_grabber%
REM python RippedTracks.py "%~1"
REM POPD
SHIFT /2
GOTO MAIN


REM        ----------------
REM  3 --> Log input track.
REM        ----------------
:STEP3
REM PUSHD %TEMP%
REM ECHO "%~1">> cdgrabber.txt
REM POPD
SHIFT /2
GOTO MAIN


REM        ------------
REM  4 --> Exit script.
REM        ------------
:THE_END
IF DEFINED _mycp CHCP %_mycp% > NUL
SET _cp=
SET _chcp=
SET _errorlevel=
SET _grabber=
SET _me=
SET _mycp=
SET _myparent=
ENDLOCAL
EXIT /B %_errorlevel%
