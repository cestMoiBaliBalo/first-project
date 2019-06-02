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
SET _cp=1252


REM ===============
REM Main algorithm.
REM ===============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL
CLS


:MAIN
IF "%~1" EQU "" (
    SET _cp=
    SET _me=
    SET _myparent=
    ENDLOCAL
    ECHO:
    ECHO:
    PAUSE
    EXIT /B 0
)
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
SET _count=counts.txt
SET _drive=%~2
SET _drive=%_drive:\=/%
PUSHD %TEMP%
DEL %_count% 2> NUL
PUSHD G:\Computing\MyPythonProject\Tasks\Extensions
python main.py "%_drive%" && python print.py
IF ERRORLEVEL 1 (
    POPD
    IF EXIST %_count% TYPE %_count%
)
POPD
SET _count=
SET _drive=
SHIFT
SHIFT
GOTO MAIN


:STEP3
PUSHD %_PYTHONPROJECT%\Tasks\Directories
python main.py "%~2"
POPD
SHIFT
SHIFT
GOTO MAIN


:STEP4
SET _target=target.txt
SET _targetid= 
PUSHD %TEMP%
DEL %_target% 2> NUL
python %_PYTHONPROJECT%\Backup\target.py "%~2"
IF NOT EXIST "%_target%" GOTO END4
FOR /F "usebackq" %%A IN ("%_target%") DO SET _targetid=%%A
IF [%_targetid%] EQU [0] GOTO END4
"C:/Program Files/Areca/areca_cl.exe" backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.music/%_targetid%.bcfg"
:END4
POPD
SET _targetid=
SET _target=
SHIFT
SHIFT
GOTO MAIN


:STEP5
SET _xxcopy=xxcopy.cmd
PUSHD C:\Computing\Python
python -m shared.shared "%~2"
PUSHD %TEMP%
IF EXIST "%_xxcopy%" (
    CALL "%_xxcopy%"
    PUSHD %_PYTHONPROJECT%
    python -m Applications.Tables.Tasks.shared "123456800" "update"
    POPD
)
POPD
POPD
SET _xxcopy=
SHIFT
SHIFT
GOTO MAIN
