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
SET _chcp=
SET _mycp=
SET _cp=1252
SET _errorlevel=0


REM ============
REM Main script.
REM ============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

SET _path=!PATH!
SET path=%_PYTHONPROJECT%\VirtualEnv\venv38;!PATH!
PUSHD %_PYTHONPROJECT%\Backup
python count.py "%~1"
IF ERRORLEVEL 1 GOTO END2
IF ERRORLEVEL 0 (
    RMDIR "%~1" /S /Q 2> NUL
    RMDIR "%~1_data" /S /Q 2> NUL
)

:END2
POPD
SET path=!_path!
SET _path=

:END1
IF DEFINED _mycp CHCP %_mycp% > NUL
SET _cp=
SET _chcp=
SET _me=
SET _mycp=
SET _myparent=
(
    SET _errorlevel=
    ENDLOCAL
    EXIT /B %_errorlevel%
)
