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


CLS


:MAIN
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
PUSHD %_PYTHONPROJECT%
SET _path=%PATH%
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
python walk.py "%~2"
SET PATH=%_path%
SET _path=
POPD
SHIFT
SHIFT
GOTO MAIN


:STEP4

:STEP4A
PUSHD %_PYTHONPROJECT%\Backup
SET _targetid=
SET _path=%PATH%
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
python target.py "%~2"
SET PATH=%_path%
IF EXIST %_TMPTXT% FOR /F "usebackq delims=|" %%A IN ("%_TMPTXT%") DO SET _targetid=%%A
IF DEFINED _targetid (
    PUSHD C:\Program Files\Areca
    areca_cl.exe backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%\workspace.music\%_targetid%.bcfg"
    POPD
)

:STEP4B
FOR /F "usebackq" %%A IN ('%_TMPTXT%') DO RMDIR %%~dpA /S /Q 2> NUL
PUSHD ..
SET _path=%PATH%
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
python temporaryenv.py > NUL
SET PATH=%_path%
POPD

:STEP4C
SET _path=
SET _targetid=
POPD
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
SET _chcp=
SET _cp=
SET _me=
SET _mycp=
SET _myparent=
ENDLOCAL
ECHO:
ECHO:
PAUSE
EXIT /B 0
