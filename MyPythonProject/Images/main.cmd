@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Development"


@CHCP 65001 > NUL
@CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
IF NOT EXIST "%~1" (
    ENDLOCAL
    EXIT /B 100
)
SET _ok=0
IF [%~2] EQU [DISPLAY] SET _ok=1
IF [%~2] EQU [INSERT] SET _ok=1
IF [%~2] EQU [RENAME] SET _ok=1
IF %_ok% EQU 0 (
    ENDLOCAL
    EXIT /B 100
)


REM ==================
REM Initializations 1.
REM ==================
SET _caller=%~nx0
SET _me=%~n0
SET _myparent=%~dp0
FOR /F "usebackq delims=" %%A IN ('%_myparent%.') DO SET _myancestor=%%~dpA


REM ==================
REM Initializations 2.
REM ==================
SET _errorlevel=0
SET _path="%~1"
SET _action=%~2


REM ============
REM Main script.
REM ============
PUSHD %_myparent:~0,-1%
CALL images.cmd
SET _errorlevel=%ERRORLEVEL%
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
