@ECHO off


@REM __author__ = Xavier ROSSET
@REM __maintainer__ = Xavier ROSSET
@REM __email__ = xavier.python.computing@protonmail.com
@REM __status__ = Production


@CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _argument=
SET _errorlevel=0


REM ==================
REM Initializations 3.
REM ==================
SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent:~0,-1%


REM ============
REM Main script.
REM ============
IF [%~3] EQU [T] SET _argument= --test
python MyPythonProject\Tasks\johndoe.py "%~1" %~2%_argument%
SET _errorlevel=%ERRORLEVEL%


REM ============
REM Exit script.
REM ============

:END2
ECHO:
ECHO:
ECHO %_errorlevel% file(s) copied to %~2 repository.
ECHO:
ECHO:
PAUSE

:END1
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
