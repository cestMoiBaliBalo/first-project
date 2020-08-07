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


REM    ==================
REM B. Initializations 2.
REM    ==================
SET _arguments=
SET _errorlevel=1
SET _cp=65001


REM    ==================
REM C. Initializations 3.
REM    ==================
PUSHD %_myparent:~0,-1%


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


REM -----
:LOOP
(
    IF [%2] NEQ [] SET _arguments=!_arguments! "%~2"
    IF [%2] EQU [] GOTO NEXT
)
SHIFT /2
GOTO LOOP


REM -----
:NEXT
ECHO: %_arguments%
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%~nx0
)
(

    REM Local Windows environment production process.
    IF %~1 EQU 1 (
        SET PATH=%_myancestor%VirtualEnv\venv38\Scripts;!PATH!
        CALL grab_beg.cmd%_arguments%
        SET _errorlevel=!ERRORLEVEL!
    )

    REM Local Windows environment unit tests.
    IF %~1 EQU 2 (
        SET PATH=%_myancestor%VirtualEnv\venv38\Scripts;!PATH!
        SET _verbose=1
        CALL grab_test.cmd%_arguments%
        SET _errorlevel=!ERRORLEVEL!
    )

    REM Travis-CI Windows environment unit tests.
    IF %~1 EQU 3 (
        SET _verbose=0
        CALL grab_test.cmd%_arguments%
        SET _errorlevel=!ERRORLEVEL!
    )
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
