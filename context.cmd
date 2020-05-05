@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
PUSHD %_COMPUTING%


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _cp=1252


REM ===============
REM Main algorithm.
REM ===============

REM Set code page.
SET _chcp=
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

REM Get code page.
SET _chcp=
SET _step=1
CALL shared.cmd
IF DEFINED _chcp ECHO Code page is %_chcp%.


:MAIN
CLS
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
SETLOCAL
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_PYTHONPROJECT%
python walk.py "%~2"
POPD
ENDLOCAL
ECHO:
ECHO:
PAUSE
SHIFT
SHIFT
GOTO MAIN


:STEP4
SETLOCAL ENABLEEXTENSIONS
SET _index=0
SET _targetid=
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_PYTHONPROJECT%

:STEP4A

REM -----
FOR /F "usebackq tokens=*" %%A IN (`python temporaryenv.py dir -f`) DO (
    IF !_index! EQU 0 SET _tempdir=%%A
    IF !_index! EQU 1 SET _tempfil=%%A
    SET /A "_index+=1"
)

REM -----
IF DEFINED _tempfil IF EXIST %_tempfil% (
    PUSHD Backup
    python target.py "%~2" %_tempfil%
    POPD
    FOR /F "usebackq delims=|" %%A IN ("%_tempfil%") DO SET _targetid=%%A
)

REM -----
IF DEFINED _targetid (
    PUSHD %PROGRAMFILES%\Areca
    areca_cl.exe backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%\workspace.music\%_targetid%.bcfg"
    POPD
)

:STEP4B
IF DEFINED _tempdir IF EXIST %_tempdir% RMDIR %_tempdir% /S /Q 2> NUL

:STEP4C
ECHO:
ECHO:
PAUSE
POPD
ENDLOCAL
SHIFT
SHIFT
GOTO MAIN


:THE_END
IF DEFINED _mycp CHCP %_mycp% > NUL
POPD
ENDLOCAL
CLS
EXIT /B 0
