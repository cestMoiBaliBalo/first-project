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
    IF [%2] EQU [] GOTO MAIN
)
SHIFT /2
GOTO LOOP


REM -----
:MAIN
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%~nx0
    SET _action=%~1
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
        PUSHD %TEMP%
        python -m Applications.Tables.tables database.db 
        POPD
        SET _verbose=1
        CALL grab_test.cmd%_arguments%
        SET _errorlevel=!ERRORLEVEL!
        PUSHD %TEMP%
        DEL database.db > NUL 2>&1
        DEL default_*.txt > NUL 2>&1
        DEL sbootleg1_*.txt > NUL 2>&1
        DEL sequences.json > NUL 2>&1
        POPD
    )

    REM Travis-CI Windows environment unit tests.
    REM Create at first the logging directory to allow Travis-CI to run logging.
    REM Create then the local audio database into the appropriate directory.
    IF %~1 EQU 3 (
        PUSHD ..\..\..
        MKDIR Log
        POPD
        PUSHD %TEMP%
        python -m Applications.Tables.tables database.db 
        POPD
        SET _verbose=0
        CALL grab_test.cmd%_arguments%
        SET _errorlevel=!ERRORLEVEL!
        PUSHD %TEMP%
        DEL database.db > NUL 2>&1
        DEL default_*.txt > NUL 2>&1
        DEL sbootleg1_*.txt > NUL 2>&1
        DEL sequences.json > NUL 2>&1
        POPD
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
