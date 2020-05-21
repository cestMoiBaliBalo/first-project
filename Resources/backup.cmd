@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%



REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _arguments=
SET _cp=1252
SET _first=1
SET _output=%TEMP%\backup.txt


REM ============
REM Main script.
REM ============

REM -----
PUSHD %_RESOURCES%
SET _step=1
CALL shared.cmd
IF DEFINED _chcp IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
POPD

REM -----
DEL %_output% 2> NUL

REM -----
IF [%~2] EQU [] IF %_first% EQU 1 GOTO STEP4


REM    ----------
REM A. Java step.
REM    ----------
REM    Enumerate files.
PUSHD %_COMPUTING%\MyJavaProject
IF NOT EXIST "targets.txt" (
    ECHO Targets repository ("%_COMPUTING%\MyJavaProject\targets.txt"^) can't be found. Please check^^!
    POPD
    GOTO STEP4
)
:STEP1
IF [%~2] EQU [] (
    POPD
    GOTO STEP2
)
SET _arguments=%_arguments% %~2
SET _first=0
FOR /F "usebackq eol=# tokens=1-4 delims=`" %%A IN ("targets.txt") DO (
    IF [%%~A] EQU [%~2] (
        SET _target=%%~A
        SET _environment=%%~B
        SET _path=%%~C
        SET _regex=%%~D
        SET _command="!_path!" "!_target!" "!_environment!" --output "%_output%"
        IF DEFINED _regex SET _command=!_command! --regex "!_regex!"
        PUSHD out\production\MyJavaProject
        java com.xavier.computing.Finder !_command! > NUL
        POPD
    )
)
SHIFT /2
GOTO STEP1


REM    ------------
REM B. Python step.
REM    ------------
REM    Check if backup is required.
:STEP2
IF NOT EXIST %_output% GOTO STEP4
PUSHD %_PYTHONPROJECT%

REM ----- B.1. Define 3.8 as python interpreter.
ECHO PATH is composed of the following directories.
ECHO:
CALL :GET_PATHS
ECHO:
ECHO:
PAUSE

REM ----- B.2. Run checker.
CLS
PUSHD Backup
python check.py "%_output%" "\.(?:ape|dsf|flac)$" --pprint

REM ----- B.3. Backup isn't required.
IF ERRORLEVEL 100 (
    POPD
    POPD
    ECHO Backup isn't required^^!
    ECHO:
    ECHO:
    PAUSE
    GOTO STEP3
)

REM ----- B.4. Backup is required.
ECHO:
ECHO:
CHOICE /C YN /N /CS /T 30 /D N /M "An additional backup is required. Would you like to run it? Press [Y] for Yes or [N] for No. "

REM ----- B.5. Backup is aborted.
IF ERRORLEVEL 2 (
    POPD
    POPD
    GOTO STEP3
)

REM ----- B.6. Confirm backup.
CLS
ECHO The following backup command will be run: python main.py -c %~1%_arguments%
ECHO:
ECHO:
CHOICE /C YN /N /CS /T 30 /D N /M "Would you like to continue? Press [Y] for Yes or [N] for No. "
IF ERRORLEVEL 2 (
    POPD
    POPD
    GOTO STEP3
)
python main.py -c %~1%_arguments%
POPD
POPD
ECHO:
ECHO:
PAUSE


REM    --------------
REM C. End of script.
REM    --------------

REM -----
:STEP3
(
    ENDLOCAL
    CLS
    ECHO PATH is now composed of the following folders.
    ECHO:
    CALL :GET_PATHS
    ECHO:
    ECHO:
    PAUSE
    CLS
    EXIT /B 0
)

REM -----
:STEP4
(
    ECHO:
    ECHO:
    PAUSE
    ENDLOCAL
    CLS
    EXIT /B 0
)


REM ================
REM Local functions.
REM ================


REM =====================================
REM GET THE LIST OF PATHS COMPOSING PATH.
REM =====================================
:GET_PATHS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _index=0
SET _path=%PATH%
:R01_LOOP
FOR /F "usebackq tokens=1* delims=;" %%A IN ('!_path!') DO (
    SET /A "_index+=1"
    IF !_index! LEQ 9 ECHO    !_index!. %%A
    IF !_index! GTR 9 IF !_index! LEQ 99 ECHO   !_index!. %%A
    IF !_index! GTR 99 IF !_index! LEQ 999 ECHO  !_index!. %%A
    SET _path=%%B
    GOTO R01_LOOP
)
ENDLOCAL
EXIT /B 0
