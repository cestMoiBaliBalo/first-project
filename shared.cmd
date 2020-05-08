@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


REM ==============================================
REM Load variables taken from the calling context.
REM ==============================================
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _step=%_step%
)


REM ================
REM Initializations.
REM ================
SET _me=%~n0
SET _myparent=%~dp0


REM  ======================
REM  Run requested routine.
REM  ======================
:MAIN

REM -----
IF %_step% EQU 1 CALL :GET_CODEPAGE
IF %_step% EQU 1 (
    ENDLOCAL
    SET _chcp=%_chcp%
)

REM -----
IF %_step% EQU 2 CALL :GET_SUFFIX
IF %_step% EQU 2 (
    ENDLOCAL
    SET _index=%_index%
    SET _suffix=%_suffix%
)

REM -----
IF %_step% EQU 3 CALL :GET_SWITCH
IF %_step% EQU 3 (
    ENDLOCAL
    SET _flag=%_flag%
    SET _switch=%_switch%
)

REM -----
IF %_step% EQU 4 CALL :CHECK_TASK
IF %_step% EQU 4 (
    ENDLOCAL
    SET _errorlevel=%_errorlevel%
)

REM -----
IF %_step% EQU 5 CALL :UPDATE_TASK
IF %_step% EQU 5 (
    ENDLOCAL
    SET _errorlevel=%_errorlevel%
)
REM -----
EXIT /B 0


:GET_CODEPAGE
SETLOCAL
SET _chcp=
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
(
    ENDLOCAL
    SET _chcp=%_chcp%
)
EXIT /B 0


:GET_SUFFIX
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _suffixes=ABCDEFGHIJKLMNOPQRSTUVWXYZ
SET _suffix=
IF %_index% LEQ 26 (
    SET _suffix=!_suffixes:~%_index%,1!
    SET /A "_index+=1"
)
(
    ENDLOCAL
    SET _index=%_index%
    SET _suffix=%_suffix%
)
EXIT /B 0


:GET_SWITCH
SETLOCAL ENABLEEXTENSIONS
SET _switch=/EC
IF %_flag% EQU 1 SET _switch=/CE
IF %_flag% EQU 0 SET _flag=1
(
    ENDLOCAL
    SET _flag=%_flag%
    SET _switch=%_switch%
)
EXIT /B 0


:CHECK_TASK
SETLOCAL
python -m Applications.Tables.Tasks.shared %_taskid% check --delta %_delta%
SET _errorlevel=%ERRORLEVEL%
(
    ENDLOCAL
    SET _errorlevel=%_errorlevel%
)
EXIT /B 0


:UPDATE_TASK
SETLOCAL
python -m Applications.Tables.Tasks.shared %_taskid% update
SET _errorlevel=%ERRORLEVEL%
(
    ENDLOCAL
    SET _errorlevel=%_errorlevel%
)
EXIT /B 0
