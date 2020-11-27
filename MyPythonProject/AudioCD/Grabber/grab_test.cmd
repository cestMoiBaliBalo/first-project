@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@IF NOT DEFINED _caller (
    ECHO off
    CLS
    CHCP 65001 > NUL
)


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0
SET _ancestor=%_myparent%
FOR /L %%A IN (1, 1, 2) DO (
    FOR /F "usebackq delims=" %%B IN ('!_ancestor!.') DO SET _myancestor=%%~dpB
    SET _ancestor=!_myancestor!
)


REM    ==================
REM B. Initializations 2.
REM    ==================
@IF NOT DEFINED _caller (
    SET PATH=%_myancestor%VirtualEnv\venv38\Scripts;!PATH!
    SET _verbose=1
    PUSHD %_myparent:~0,-1%
)


REM    ==================
REM C. Initializations 3.
REM    ==================
SET _ko=
SET _index=
SET _errorlevel=
SET _runner_0=runner.py
SET _runner_1=textrunner.py -vv


REM    ===========
REM D. Main logic.
REM    ===========


@REM /* MAIN CONTEXT BEGIN ---------- */
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%~nx0
    SET _path=%~dp0
)
@ECHO _path stores "%_path%".
@ECHO:
@ECHO:


@REM -----
@SET _index=0
@SET _ko=0


@REM -----
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@SET _path=%PATH%
@ECHO --------------------
@ECHO Runtime environment.
@ECHO --------------------
@ECHO:
:LOOP
@FOR /F "usebackq tokens=1,* delims=;" %%A IN ('!_path!') DO (
    SET /A "_index+=1"
    IF !_index! LEQ 99 SET _line=!_index!. %%A
    IF !_index! LEQ 9 SET _line= !_index!. %%A
    ECHO !_line!
    SET _path=%%B
    GOTO LOOP
)
@ECHO:
@ECHO:
@ECHO:
ENDLOCAL


@REM /* CONTEXT 1 BEGIN ---------- */
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _jsontags=%TEMP%\tags.json
FOR /L %%A IN (1, 1, 2) DO FOR %%A IN ("!_path!.") DO SET _path=%%~dpA
PUSHD %_path:~0,-1%
COPY /Y Applications\Unittests\Resources\sequences.json %TEMP% > NUL 2>&1
@IF %_verbose% EQU 1 (
    ECHO -----------------------------------------
    ECHO Audio CDs ripping application unit tests.
    ECHO -----------------------------------------
    ECHO:
)
FOR /F "usebackq eol=# tokens=1*" %%A IN ("Applications\Unittests\Resources\audiotags.txt") DO (
    IF EXIST "%%~A" (
        SET /A "_index+=1"
        COPY /Y "%%~A" %TEMP% > NUL 2>&1
        CALL AudioCD\Grabber\grab_beg.cmd "%TEMP%\%%~nxA" %%B
        SET _errorlevel=!ERRORLEVEL!
        IF %_verbose% EQU 1 IF !_errorlevel! EQU 0 ECHO Test !_index! ... ok
        IF %_verbose% EQU 1 IF !_errorlevel! NEQ 0 ECHO Test !_index! ... ko
        IF !_errorlevel! NEQ 0 SET _ko=1
    )
)
@ECHO:
@ECHO:
@IF EXIST %_jsontags% (
    python AudioCD\Grabber\insertDiscs.py %_jsontags%
    IF ERRORLEVEL 1 DEL %_jsontags% 2>NUL
)
SETLOCAL
@IF DEFINED _action IF %_action% EQU 2 (
    PUSHD ..
    CALL insertDigitalDiscs.cmd "F:\U\U2\1\2000 - All That You Can’t Leave Behind (20th Anniversary Edition)\CD1\1.Free Lossless Audio Codec" T
    POPD
)
ENDLOCAL
POPD


@REM /* CONTEXT 1 END ------------------------------------ */
@REM /* Preserve _errorlevel value into the upper context. */
(
    ENDLOCAL
    SET _errorlevel=%_ko%
)


REM Failure: abort unit tests.
IF %_errorlevel% EQU 1 GOTO THE_END


@REM /* CONTEXT 2 BEGIN ---------- */
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@IF %_verbose% EQU 1 (
    ECHO ---------------------------------------------------
    ECHO Lossless digital audio files conversion unit tests.
    ECHO ---------------------------------------------------
    ECHO:
)
FOR /L %%A IN (1, 1, 2) DO FOR %%A IN ("!_path!.") DO SET _path=%%~dpA
PUSHD %_path:~0,-1%
FOR /F "usebackq eol=# tokens=1*" %%A IN ("Applications\Unittests\Resources\batchconverter.txt") DO (
    IF EXIST "%%~A" (
        SET /A "_index+=1"
        COPY /Y "%%~A" %TEMP% > NUL 2>&1
        CALL AudioCD\Converter\convert_track.cmd "%TEMP%\%%~nxA" %%B
        SET _errorlevel=!ERRORLEVEL!
        IF %_verbose% EQU 1 IF !_errorlevel! EQU 0 ECHO Test !_index! ... ok
        IF %_verbose% EQU 1 IF !_errorlevel! NEQ 0 ECHO Test !_index! ... ko
        IF !_errorlevel! NEQ 0 SET _ko=1
    )
)
@ECHO:
@ECHO:
POPD


@REM /* CONTEXT 2 END ------------------------------------ */
@REM /* Preserve _errorlevel value into the upper context. */
(
    ENDLOCAL
    SET _errorlevel=%_ko%
)


REM Failure: abort unit tests.
IF %_errorlevel% EQU 1 GOTO THE_END


@REM /* MAIN CONTEXT END --------------------------------- */
@REM /* Preserve _errorlevel value into the upper context. */
(
    IF %_verbose% EQU 1 ECHO _path stores "%_path%".
    ENDLOCAL
    IF %_verbose% EQU 1 ECHO _path stores "!_path!".
    SET _errorlevel=%_errorlevel%
)
@IF %_verbose% EQU 1 IF NOT DEFINED _path ECHO _path is now undefined.
@ECHO:
@ECHO:


REM Success: run python unit tests.
@IF %_verbose% EQU 1 (
    ECHO --------------------------
    ECHO Python scripts unit tests.
    ECHO --------------------------
    ECHO:
)
PUSHD ..\..
python !_runner_%_verbose%!
SET _errorlevel=%ERRORLEVEL%
POPD
IF %_errorlevel% EQU 1 GOTO THE_END


REM    ============
REM E. Exit script.
REM    ============
:THE_END
@IF NOT DEFINED _caller POPD
(
    ENDLOCAL
    IF %_verbose% EQU 1 (
        ECHO:
        ECHO:
    )
    ECHO Script exited with code %_errorlevel%.
    IF %_verbose% EQU 1 IF %_errorlevel% EQU 0 (
        ECHO:
        ECHO ^^!^^!^^! Changes can be merged into the master branch ^^!^^!^^!
    )
    ECHO:
    ECHO:
    EXIT /B %_errorlevel%
)
