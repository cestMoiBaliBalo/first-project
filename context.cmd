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
SET _mycp=
SET _cp=1252


REM ===============
REM Main algorithm.
REM ===============

REM Set code page.
SET _chcp=
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

REM Get code page.
SET _chcp=
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp ECHO Code page is %_chcp%.


:MAIN
CLS
IF "%~1" EQU "" GOTO THE_END
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5


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
SETLOCAL ENABLEEXTENSIONS
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
SET _targetid=
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%

:STEP4A
PUSHD %_PYTHONPROJECT%\Backup
python target.py "%~2"
IF EXIST %_TMPTXT% FOR /F "usebackq delims=|" %%A IN ("%_TMPTXT%") DO SET _targetid=%%A
IF DEFINED _targetid (
    PUSHD C:\Program Files\Areca
    areca_cl.exe backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%\workspace.music\%_targetid%.bcfg"
    POPD
)

:STEP4B
FOR /F "usebackq" %%A IN ('%_TMPTXT%') DO RMDIR %%~dpA /S /Q 2> NUL
PUSHD ..
python temporaryenv.py > NUL
POPD

:STEP4C
POPD
ENDLOCAL
ECHO:
ECHO:
PAUSE
SHIFT
SHIFT
GOTO MAIN


:STEP5
SHIFT
SHIFT
GOTO MAIN


:THE_END
IF DEFINED _mycp CHCP %_mycp% > NUL
SET _cp=
SET _me=
SET _chcp=
SET _mycp=
SET _myparent=
ENDLOCAL
EXIT /B 0
