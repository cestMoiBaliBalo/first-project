@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
PUSHD %_RESOURCES%


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
SET _areca=%PROGRAMFILES%/Areca/areca_cl.exe


REM ============
REM Main script.
REM ============
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

:MENU
IF [%~1] EQU [1] GOTO STEP1
IF [%~1] EQU [2] GOTO STEP2
IF [%~1] EQU [] GOTO THE_END
SHIFT
GOTO MENU

:STEP1
"%_areca%" backup -c -wdir %TEMP%\tmp-Xavier -config %_BACKUP%/workspace.documents/1832340664.bcfg
SHIFT
GOTO MENU

:STEP2
SHIFT
GOTO MENU

:THE_END
(
    ECHO:
    ECHO:
    PAUSE
    IF DEFINED _mycp CHCP %_mycp% > NUL
    POPD
    ENDLOCAL
    CLS
    EXIT /B %_errorlevel%
)
