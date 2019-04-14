 @ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _decorators=
SET _grabber=grabber.txt
SET _idtags=idtags.txt


REM ===========
REM Main logic.
REM ===========
PUSHD %TEMP%

REM Log both date and time.
ECHO = %DATE% - %TIME% =================================================>> %_grabber%
ECHO %~1>> %_grabber%
ECHO %~2>> %_grabber%
ECHO %~3>> %_grabber%
ECHO %~4>> %_grabber%

REM Log input tags.
ECHO = %DATE% - %TIME% =================================================>> %_idtags%
TYPE "%~1">> %_idtags%

REM Alter tags.
PUSHD "%_PYTHONPROJECT%\AudioCD\Grabber"
:LOOP
IF [%~5] NEQ [] (
    SET _decorators=!_decorators!%5 
    SHIFT /5
    GOTO LOOP
)
python Main.py "%~1" %~2 "%~3" %_decorators%--tags_processing %~4
POPD

REM Exit script.
POPD
SET _decorators=
SET _grabber=
SET _idtags=
SET _me=
SET _myparent=
ENDLOCAL
EXIT /B 0
