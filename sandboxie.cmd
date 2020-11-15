@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


@REM ==================
@REM Initializations 1.
@REM ==================
SET _me=%~n0
SET _myparent=%~dp0


@REM ==================
@REM Initializations 2.
@REM ==================
SET _mycp=
SET _cp=1252


@REM ============
@REM Main script.
@REM ============


@REM     -----------------------------------------------------
@REM  1. Allow interface to decode Latin-1 encoded characters.
@REM     -----------------------------------------------------
PUSHD %_myparent%Resources

@REM     Set code page.
SET _chcp=
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

@REM     Get code page.
SET _chcp=
SET _step=1
CALL shared.cmd
IF DEFINED _mycp ECHO Code page is currently %_mycp%.
IF DEFINED _chcp ECHO Code page set to %_chcp%.

@REM     Check characters encoding.
ECHO Les caractères accentués sont restitués proprement ^^!
FOR /F "usebackq tokens=*" %%A IN ("accentuated.txt") DO ECHO %%A

POPD



@REM     -------------------
@REM  2. Run requested task.
@REM     -------------------
:MAIN
IF "%~1" EQU "" GOTO THE_END
IF "%~1" EQU "1" GOTO STEP1
SHIFT
GOTO MAIN


@REM     -------------------------------
@REM  3. Delete GNUCash sandbox content.
@REM     -------------------------------
:STEP1
SETLOCAL
SET _taskid=123456798
SET _delta=8
CALL :CHECK_TASK
IF ERRORLEVEL 1 (
    @ECHO:
    @ECHO:
    @ECHO ===============================
    @ECHO Delete GNUCash sandbox content.
    @ECHO ===============================
    "%PROGRAMFILES%\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && @ECHO GNUCash sandbox content successfully removed.
    CALL :UPDATE_TASK
)
ENDLOCAL
SHIFT
GOTO MAIN


@REM ==============
@REM End of script.
@REM ==============
:THE_END
ECHO:
ECHO:
IF DEFINED _mycp (
    CHCP %_mycp% > NUL
    ECHO Code page restored to %_mycp%.
)
ENDLOCAL
REM PAUSE
REM CLS
EXIT /B %ERRORLEVEL%


@REM =================
@REM Shared functions.
@REM =================
:CHECK_TASK
SETLOCAL
python -m Applications.Tables.Tasks.shared %_taskid% check --delta %_delta%
(
    ENDLOCAL
    EXIT /B %ERRORLEVEL%
)


:UPDATE_TASK
SETLOCAL
python -m Applications.Tables.Tasks.shared %_taskid% update
(
    ENDLOCAL
    EXIT /B %ERRORLEVEL%
)
