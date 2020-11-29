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
SET _mycp=
SET _cp=65001
SET _errorlevel=0
SET _areca=%PROGRAMFILES%\Areca\areca_cl.exe


REM ============
REM Main script.
REM ============
PUSHD %_myparent%Resources
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

:MAIN
IF [%~1] EQU [1] GOTO STEP1
IF [%~1] EQU [2] GOTO STEP2
IF [%~1] EQU [] GOTO END
SHIFT
GOTO MAIN

:STEP1
"%_areca%" backup -c -wdir %TEMP%\tmp-Xavier -config %_BACKUP%/workspace.documents/1832340664.bcfg
SHIFT
GOTO MAIN

:STEP2
SHIFT
GOTO MAIN

:END
@IF DEFINED _mycp CHCP %_mycp% > NUL
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
