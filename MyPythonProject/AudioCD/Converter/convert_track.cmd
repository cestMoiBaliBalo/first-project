@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"

@REM :param 1: Audio tags plain text file.
@REM :param 2: Audio encoder code. FDK or LAME.
@REM :param 3: Audio tags decorators. AlbumSort, EncodedFromHDtracksFLAC, etc.


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
SET _ancestor=%_myparent%
FOR /L %%A IN (1, 1, 2) DO (
    FOR /F "usebackq delims=" %%B IN ('!_ancestor!.') DO SET _myancestor=%%~dpB
    SET _ancestor=!_myancestor!
)
SET _ancestor=


REM    ==================
REM B. Initializations 2.
REM    ==================
@IF NOT DEFINED _caller SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
PUSHD %_myparent:~0,-1%


REM    ==================
REM C. Initializations 3.
REM    ==================
SET _index=0
SET _decorators=
SET _errorlevel=
SET _encoder=
SET _track=


REM    ============
REM D. Main script.
REM    ============

REM    Backup input tags.
PUSHD ..\Grabber
FOR /F "usebackq" %%A IN (`python getTrack.py "%~1"`) DO (
    IF [%%A] NEQ [] (
        SET /A "_index+=1"
        IF !_index! EQU 1 (
            SET _track=%%A
            IF !_track! LEQ 9 SET _track=0!_track!
        )
        IF !_index! EQU 2 SET _encoder=%%A
    )
)
POPD
IF DEFINED _encoder IF DEFINED _track COPY /Y "%~1" %TEMP%\%~n1_T%_track%_%_encoder%%~x1 > NUL 2>&1
IF NOT DEFINED _encoder IF DEFINED _track COPY /Y "%~1" %TEMP%\%~n1_T%_track%%~x1 > NUL 2>&1

REM    Alter tags respective to the ripping profile.
python convertTrack.py %*
SET _errorlevel=%ERRORLEVEL%

REM    Backup output tags.
IF %_errorlevel% EQU 0 (
    IF DEFINED _encoder IF DEFINED _track COPY /Y "%~1" %TEMP%\%~n1_T%_track%_%_encoder%_out%~x1 > NUL 2>&1
    IF NOT DEFINED _encoder IF DEFINED _track COPY /Y "%~1" %TEMP%\%~n1_T%_track%_out%~x1 > NUL 2>&1
)


REM    ============
REM E. Exit script.
REM    ============
POPD
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
