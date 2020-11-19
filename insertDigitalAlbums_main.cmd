@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


@CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0
SET _caller=%~nx0


REM ==================
REM Initializations 2.
REM ==================
SET _errorlevel=0
SET _records=


REM ============
REM Main script.
REM ============

REM ----- Get albums path.
SET /P _path="Please type the album path (you can press TAB for path expansion): "
FOR /F "usebackq delims=" %%A IN ('!_path!') DO SET _path="%%~A"
CLS
IF NOT EXIST %_path% (
    SET _errorlevel=-1
    GOTO END
)
PUSHD %_myparent:~0,-1%
CALL insertDigitalAlbums.cmd %_path%
SET _records=%ERRORLEVEL%
@IF %_records% GEQ 0 (
    ECHO:
    ECHO:
    ECHO %_records% record(s^) inserted into the local audio database.
    ECHO:
    ECHO:
    ECHO:
    PAUSE
    CLS
)
POPD

REM ----- Exit script.
:END
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
