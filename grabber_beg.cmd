@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


@REM ==================
@REM Initializations 1.
@REM ==================
SET _me=%~n0
SET _myparent=%~dp0


@REM ==================
@REM Initializations 2.
@REM ==================
SET _decorators=
SET _grabber=grabber.txt
SET _idtags=idtags.txt


@REM ===========
@REM Main logic.
@REM ===========
@REM PUSHD %TEMP%

@REM Log both date and time.
@REM ECHO = %DATE% - %TIME% =================================================>> %_grabber%
@REM ECHO %~1>> %_grabber%
@REM ECHO %~2>> %_grabber%
@REM ECHO %~3>> %_grabber%
@REM ECHO %~5>> %_grabber%

@REM Log input tags.
@REM ECHO = %DATE% - %TIME% =================================================>> %_idtags%
@REM TYPE "%~1">> %_idtags%

@REM Alter tags.
:LOOP
IF [%~6] NEQ [] (
    SET _decorators=!_decorators!%6 
    SHIFT /6
    GOTO LOOP
)
PUSHD "%_PYTHONPROJECT%\AudioCD\Grabber"
python Grab.py "%~1" %~2 %~3 %_decorators%--tags_processing %~5
POPD

@REM Exit script.
@REM POPD
SET _decorators=
SET _grabber=
SET _idtags=
SET _me=
SET _myparent=
ENDLOCAL
EXIT /B 0
