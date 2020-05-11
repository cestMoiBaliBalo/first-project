@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_COMPUTING%


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _ok=0
SET _chcp=
SET _mycp=
SET _date=
SET _cp=1252
SET _errorlevel=0


REM ============
REM Main script.
REM ============
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)
IF [%~1] EQU [I] SET _ok=1
IF [%~1] EQU [B] SET _ok=1
IF %_ok% EQU 0 GOTO END1

SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _taskid=123456802
SET _delta=7
SET _index=0
SET _step=4
SET _errorlevel=
CALL shared.cmd
IF DEFINED _errorlevel IF %_errorlevel% EQU 1 (
    PUSHD MyPythonProject\Tasks\Manager
    FOR /F "usebackq" %%A IN (`python merge.py "1" "add"`) DO (
        SET /A "_index+=1"
        IF !_index! EQU 2 SET _date=%%A
    )
    POPD
    IF DEFINED _date (
        "%PROGRAMFILES%/Areca/areca_cl.exe" merge -k -c -wdir %TEMP%\tmp-Xavier -config %_BACKUP%/workspace.documents/1832340664.bcfg -date !_date!
        IF ERRORLEVEL 1 (
            ENDLOCAL
            GOTO END2
        )
        SET _step=5
        CALL shared.cmd
    )
)
ENDLOCAL


REM ============
REM Exit script.
REM ============

:END2
IF DEFINED _mycp CHCP %_mycp% > NUL
IF [%~1] EQU [I] PAUSE

:END1
(
    POPD
    ENDLOCAL
    CLS
    EXIT /B %_errorlevel%
)
