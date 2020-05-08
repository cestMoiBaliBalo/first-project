@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _chcp=
SET _mycp=
SET _count=0
SET _cp=1252
SET _errorlevel=0


REM ============
REM Main script.
REM ============
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

:MAIN
PUSHD "%~1"
FOR /R %%A IN (*.*) DO SET /A "_count+=1"
POPD
IF %_count% EQU 0 (
    RMDIR "%~1" /S /Q
    RMDIR "%~1_data" /S /Q 2> NUL
)

:END
IF DEFINED _mycp CHCP %_mycp% > NUL
(
    ENDLOCAL
    CLS
    EXIT /B %_errorlevel%
)
