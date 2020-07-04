@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@IF NOT DEFINED _caller (
    ECHO off
    CLS
    CHCP 65001 > NUL
)


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0


REM    ==================
REM B. Initializations 2.
REM    ==================
@IF NOT DEFINED _caller (
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    SET _verbose=1
    PUSHD %_myparent:~0,-1%
)


REM    ==================
REM C. Initializations 3.
REM    ==================
SET _index=0
SET _errorlevel=
SET _runner_0=runner.py
SET _runner_1=textrunner.py -vv


REM    ===========
REM D. Main logic.
REM    ===========
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%~nx0
    SET _path=%~dp0
    SET _ko=0
)
FOR /L %%A IN (1, 1, 2) DO FOR %%A IN ("!_path!.") DO SET _path=%%~dpA
PUSHD %_path:~0,-1%
FOR /F "usebackq eol=# tokens=1*" %%A IN ("Applications\Unittests\Resources\defaultalbum.txt") DO (
    IF EXIST "%%~A" (
        SET /A "_index+=1"
        COPY /Y "%%~A" %TEMP% > NUL 2>&1
        CALL AudioCD\Grabber\grab_beg.cmd "%TEMP%\%%~nxA" %%B
        SET _errorlevel=!ERRORLEVEL!
        IF %_verbose% EQU 1 IF !_errorlevel! EQU 0 ECHO Test !_index! ... ok
        IF %_verbose% EQU 1 IF !_errorlevel! NEQ 0 ECHO Test !_index! ... ko
        IF !_errorlevel! NEQ 0 SET _ko=1
    )
)
POPD
(
    ENDLOCAL
    SET _errorlevel=%_ko%
)


REM Failure: abort unit tests.
IF %_errorlevel% EQU 1 GOTO THE_END

REM Success: run python unit tests.
PUSHD ..\..
CALL python %%_runner_%_verbose%%%
SET _errorlevel=%ERRORLEVEL%
POPD
IF %_errorlevel% EQU 1 GOTO THE_END


REM    ============
REM E. Exit script.
REM    ============
:THE_END
@IF NOT DEFINED _caller POPD
(
    ENDLOCAL
    IF %_verbose% EQU 1 (
        ECHO:
        ECHO:
    )
    ECHO Script exited with code %_errorlevel%.
    ECHO:
    ECHO:
    EXIT /B %_errorlevel%
)
