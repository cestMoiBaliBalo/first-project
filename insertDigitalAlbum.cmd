@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


@SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@IF NOT DEFINED _caller (
    ECHO off
    CLS
    CHCP 65001 > NUL
)


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _album_0=
SET _album_1=default
SET _album_2=bootleg
SET _album_100=
SET _album_200=
SET _album_300=
SET _album_400=
SET _drive=%~d1


REM ============
REM Main script.
REM ============
SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent:~0,-1%

REM ----- Java step for getting the album type (default or bootleg).
PUSHD MyJavaProject\Albums\out\production\Albums
java com.computing.xavier.Main "%~1"
SET _type=%ERRORLEVEL%
IF NOT DEFINED _album_%_type% (
    SET _errorlevel=9%_type%
    POPD
    GOTO END
)
POPD

REM ----- Python step for importing tags into the local audio batabase.
(
    SET _argument=
    SHIFT /2
    IF [%~2] EQU [T] SET _argument= --test
)
PUSHD MyPythonProject\Tasks
python InsertDigitalAlbum.py !_album_%_type%! "%~1"%_argument%
SET _errorlevel=%ERRORLEVEL%
POPD
GOTO END

REM ----- Exit script.
:END
POPD
(
    ENDLOCAL
    IF NOT DEFINED _caller (
        ECHO:
        ECHO:
        IF %_errorlevel% EQU 9100 ECHO Please provide an absolute path.
        IF %_errorlevel% EQU 9200 ECHO Please provide an existing path.
        IF %_errorlevel% EQU 9300 ECHO Please provide a coherent root drive. Should be F instead of %_drive:~0,-1%^!
        IF %_errorlevel% EQU 9400 ECHO Please provide enough directories to guess the album type.
        IF %_errorlevel% GTR 0 IF %_errorlevel% LSS 9100 ECHO Disc inserted into the local audio database.
        IF %_errorlevel% EQU 0 ECHO Disc not inserted (is it already present into the local audio database?^).
        ECHO:
        ECHO:
        PAUSE
        CLS
    )
    EXIT /B %_errorlevel%
)
