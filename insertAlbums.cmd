@ECHO off
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
SET _album_0=
SET _album_1=default
SET _album_100=
SET _album_2=bootleg
SET _album_200=


REM ============
REM Main script.
REM ============
SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent:~0,-1%
IF NOT EXIST "%~1" GOTO END

REM ----- Java step.
PUSHD MyJavaProject\Albums\out\production\Albums
java com.computing.xavier.Main "%~1"
SET _type=%ERRORLEVEL%
POPD
IF NOT DEFINED _album_%_type% GOTO END

REM ----- Python step.
PUSHD MyPythonProject\Tasks
python InsertAlbums.py !_album_%_type%! "%~1"
SET _records=%ERRORLEVEL%
POPD
@ECHO:
@ECHO:
@ECHO %_records% record(s) inserted into the local audio database.
@ECHO:
@ECHO:
@ECHO:
@PAUSE

:END
POPD
ENDLOCAL
@CLS
EXIT /B 0
