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
SET _images=
SET _cmdfile=


REM ============
REM Main script.
REM ============
:MAIN
CLS
PUSHD %TEMP%
DEL cmdfile.txt 2> NUL
ECHO Script is scanning MyCloud %~1 images collection. Please be patient as it may take some time.
PUSHD "%_PYTHONPROJECT%\Images"
python Numbering.py "%~1" --debug


REM --------------
REM Rename images.
REM --------------
:RENAME
IF ERRORLEVEL 11 (
    SET _errorlevel=!ERRORLEVEL!
    CLS
    PUSHD %TEMP%
    IF EXIST cmdfile.txt (
        FOR /F "usebackq delims=| tokens=1,2" %%A IN ("cmdfile.txt") DO (
            SET _images=%%~A
            SET _cmdfile=%%~B
        )
        ECHO:
        ECHO:
        ECHO !_images! image(s^) need(s^) to be renamed. Here is the renaming script:
        ECHO:
        ECHO:

        REM --> 1. Display rename commands.
        TYPE "!_cmdfile!"

        REM --> 2. Prompt for running commands.
        CALL :QUESTION "YN" "60" "N" "Please confirm you want to run this script." _answer

        REM --> 3. Don't run commands: exit with code 11.
        IF [!_answer!] EQU [N] (
            POPD
            SET _exitcode=!_errorlevel!
            GOTO EXIT
        )

        REM --> 4. Run commands then exit with code 10.
        CLS
        CALL "!_cmdfile!"
        ECHO:
        ECHO:
        PAUSE
        POPD
        SET /A "_exitcode=_errorlevel-1"
        GOTO EXIT

    )
    POPD
    SET _exitcode=!_errorlevel!
    GOTO EXIT
)


REM ------------
REM Move images.
REM ------------
:MOVE
IF ERRORLEVEL 10 (
    SET _errorlevel=!ERRORLEVEL!
    CLS
    PUSHD %TEMP%
    IF EXIST cmdfile.txt (
        FOR /F "usebackq delims=| tokens=1,2" %%A IN ("cmdfile.txt") DO (
            SET _images=%%~A
            SET _cmdfile=%%~B
        )
        ECHO:
        ECHO:
        ECHO !_images! image(s^) need(s^) at first to be moved. Here is the moving script:
        ECHO:
        ECHO:

        REM --> 1. Display move commands.
        TYPE "!_cmdfile!"

        REM --> 2. Prompt for running commands.
        CALL :QUESTION "YN" "60" "N" "Please confirm you want to run this script." _answer

        REM --> 3. Don't run commands: exit with code 11.
        IF [!_answer!] EQU [N] (
            POPD
            SET /A "_exitcode=_errorlevel+1"
            GOTO EXIT
        )

        REM --> 4. Run commands then scan collection again for renaming images.
        CLS
        CALL "!_cmdfile!"
        ECHO:
        ECHO:
        PAUSE
        POPD
        POPD
        POPD
        GOTO MAIN

    )
    POPD
    SET /A "_exitcode=_errorlevel+1"
    GOTO EXIT
)


REM ----------------
REM No images found.
REM ----------------
:NONE
IF ERRORLEVEL 0 (
    SET _errorlevel=!ERRORLEVEL!
    CLS
    ECHO:
    ECHO:
    ECHO Any images to rename haven't been found. Script will exit. & PAUSE > NUL
    SET /A "_exitcode=_errorlevel+11"
    GOTO EXIT
)



REM -----
REM Exit.
REM -----
:EXIT
POPD
POPD
SET _images=
SET _cmdfile=
EXIT /B %_exitcode%
