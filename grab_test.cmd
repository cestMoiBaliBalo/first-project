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


REM    ==================
REM B. Initializations 2.
REM    ==================
@IF NOT DEFINED _caller (
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    PUSHD %_myparent:~0,-1%
)


REM    ==================
REM C. Initializations 3.
REM    ==================
SET _index=0
SET _cp=65001
SET _arguments=
SET _errorlevel=


REM     =====================================================
REM D. Allow interface to decode Latin-1 encoded characters.
REM     =====================================================
PUSHD Resources
SET _chcp=
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)
POPD


REM    ===========
REM E. Main logic.
REM    ===========
(
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _caller=%_me%
    SET _ko=0
)
FOR /F "usebackq eol=# tokens=1-5* delims=|" %%A IN ("MyPythonProject\Applications\Unittests\Resources\defaultalbum.txt") DO (
    IF EXIST "%%~A" (
        COPY /Y "%%~A" %TEMP% > NUL 2>&1
        SET _arguments="%TEMP%\%%~nxA" %%B %%C %%D %%E
        IF [%%~F] NEQ [] SET _arguments=!_arguments! %%F
        SET /A "_index+=1"
        CALL grab_beg.cmd !_arguments!
        SET _errorlevel=!ERRORLEVEL!
        ECHO Test !_index!. Le code retour est !_errorlevel!.
        IF !_errorlevel! NEQ 0 SET _ko=1
    )
)
(
    ENDLOCAL
    SET _errorlevel=%_ko%
)
IF %_errorlevel% EQU 1 GOTO THE_END
ECHO:
ECHO:
python -m unittest -v Applications.Unittests.module5
SET _errorlevel=%ERRORLEVEL%
IF %_errorlevel% EQU 0 (
    PUSHD %TEMP%
    DEL idtags_T*.txt > NUL 2>&1
    DEL sequences.json > NUL 2>&1
    DEL tags.json > NUL 2>&1
    POPD
)


REM    ============
REM F. Exit script.
REM    ============
:THE_END
@IF DEFINED _mycp CHCP %_mycp% > NUL
@IF NOT DEFINED _caller POPD
(
    ENDLOCAL
    ECHO:
    ECHO:
    ECHO Script exited with code %_errorlevel%.
    ECHO:
    ECHO:
    EXIT /B %_errorlevel%
)
