@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"

REM :param 1: Audio tags plain text file.
REM :param 2: Ripping profile.
REM :param 3: Audio encoder sequence.
REM :param 4: Deprecated argument.
REM :param 5: Audio data processing profile.
REM :param 6: Audio tags decorators.


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0


REM    ==================
REM B. Initializations 1.
REM    ==================
SET _grabber=grabber.txt
SET _idtags=idtags.txt
SET _decorators=


REM    ===========
REM C. Main logic.
REM    ===========
:LOOP
IF [%~6] NEQ [] (
    SET _decorators=!_decorators!%6 
    SHIFT /6
    GOTO LOOP
)
PUSHD "%_PYTHONPROJECT%\AudioCD\Grabber"
python Grab.py "%~1" %~2 %~3 %_decorators%--tags_processing %~5
POPD


REM ============
REM Exit script.
REM ============
(
    SET _me=
    SET _idtags=
    SET _grabber=
    SET _myparent=
    SET _decorators=
    ENDLOCAL
    CLS
    EXIT /B 0
)
