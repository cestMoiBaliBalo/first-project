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


REM ==================
REM Initializations 2.
REM ==================
SET _cp=65001


REM ===============
REM Main algorithm.
REM ===============
SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent%Resources

REM Set code page.
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

REM Get code page.
IF %_chcp% NEQ %_cp% (
    SET _step=1
    CALL shared.cmd
    IF DEFINED _chcp ECHO Code page was %_chcp%.
    IF DEFINED _chcp ECHO Code page set to %_cp%.
)


:MAIN
IF "%~1" EQU "" GOTO THE_END
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4


:STEP1
XXCOPY "G:\Videos\AVCHD Videos\" "%~2" /CLONE /oQ /oF2 /oS2 /oD2 /oA:%_XXCOPYLOG%
SHIFT
SHIFT
GOTO MAIN


:STEP2
SHIFT
SHIFT
GOTO MAIN


:STEP3
PUSHD ..\MyPythonProject\Tasks
@ECHO:
@ECHO:
python walkFileTree.py "%~2"
POPD
ECHO:
ECHO:
PAUSE
SHIFT
SHIFT
GOTO MAIN


:STEP4
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _first=1
SET _targetid=
PUSHD ..\MyPythonProject\Backup

REM -----
FOR /F "usebackq" %%A IN (`python target.py "%~2"`) DO (
    IF !_first! EQU 1 SET _targetid=%%A
    SET _first=0
)

REM -----
IF DEFINED _targetid (
    PUSHD %PROGRAMFILES%\Areca
    areca_cl.exe backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%\workspace.music\%_targetid%.bcfg"
    POPD
)

REM -----
ECHO:
ECHO:
PAUSE
POPD
ENDLOCAL
SHIFT
SHIFT
GOTO MAIN


:THE_END
@IF DEFINED _mycp CHCP %_mycp% > NUL
POPD
(
    ENDLOCAL
    CLS
    EXIT /B 0
)
