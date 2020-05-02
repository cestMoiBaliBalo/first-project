@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


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
SET _cp=1252
SET _errorlevel=0
SET _areca=%PROGRAMFILES%/Areca/areca_cl.exe


REM ============
REM Main script.
REM ============
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
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
IF DEFINED _mycp CHCP %_mycp% > NUL
SET _cp=
SET _me=
SET _chcp=
SET _mycp=
SET _areca=
SET _myparent=
(
    SET _errorlevel=
    ENDLOCAL
    EXIT /B %_errorlevel%
)
