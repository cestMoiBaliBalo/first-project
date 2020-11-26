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
SET _ancestor=%_myparent%
FOR /L %%A IN (1, 1, 2) DO (
    FOR /F "usebackq delims=" %%B IN ('!_ancestor!.') DO SET _myancestor=%%~dpB
    SET _ancestor=!_myancestor!
)
SET _ancestor=


REM    ==================
REM B. Initializations 2.
REM    ==================
SET _arguments=
SET _decorators=
SET _errorlevel=0
SET _cp=65001


REM    ==================
REM C. Initializations 3.
REM    ==================
PUSHD %_myparent:~0,-1%


REM    ============
REM D. Main script.
REM    ============


REM -----
PUSHD ..\..\..\Resources
SET _chcp=
SET _mycp=
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)
POPD
IF %~1 EQU 2 GOTO MAIN
IF %~1 EQU 3 GOTO MAIN


REM -----
:LOOP
(
    IF [%5] NEQ [] SET _decorators=!_decorators! "%~5"
    IF [%5] EQU [] GOTO ARGUMENTS
)
SHIFT /5
GOTO LOOP


REM -----
:ARGUMENTS
SET _arguments="%~2" "%~3"%_decorators%
IF %~4 EQU 1 SET _arguments=%_arguments% --debug


REM -----
:MAIN
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%~nx0
)
IF %~1 EQU 1 (
    SET PATH=%_myancestor%VirtualEnv\venv38\Scripts;!PATH!
    CALL convert_track.cmd %_arguments%
    SET _errorlevel=!ERRORLEVEL!
)
(
    ENDLOCAL
    SET _errorlevel=%_errorlevel%
)


REM -----
@IF DEFINED _mycp CHCP %_mycp% > NUL
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
