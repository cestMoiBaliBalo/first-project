@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


REM :param 1: tags file.
REM :param 2: ripping profile.
REM :param 3: audio encoder sequence.
REM :param 4: deprecated argument.
REM :param 5: audio data processing profile.
REM :param 6: tags decorators.


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


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
    EXIT /B 0
)
