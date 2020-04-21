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
SET _errorlevel=0
SET _grabber=%_PYTHONPROJECT%\AudioCD\Grabber
SET _jsontags=%TEMP%\tags.json
SET _jsonxreferences=%TEMP%\xreferences.json
SET _txtfiles=%_RESOURCES%\rippedtracks.txt


REM ============
REM Main script.
REM ============
SET _chcp=
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)


:MAIN
IF "%~1" EQU "" GOTO THE_END
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
SHIFT
GOTO MAIN


REM        -----------------------------------------------
REM  1 --> Append ripped tracks to digital audio database.
REM        -----------------------------------------------
:STEP1
IF EXIST "%_jsontags%" (
    SET _path=%PATH%
    SET path=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
    FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
    PUSHD !_parent!
    python Insert_Albums.py "%_jsontags%"
    POPD
    SET path=%_path%
    SET _path=
    SET _parent=
    DEL "%_jsontags%" 2>NUL
)
SHIFT
GOTO MAIN


REM        ---------------------------------------------
REM  2 --> Append ripped tracks to XReferences database.
REM        ---------------------------------------------
:STEP2
REM IF EXIST "%_jsonxreferences%" (
REM     FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
REM     PUSHD !_parent!
REM     python Insert_XReferences.py "%_jsonxreferences%"
REM     POPD
REM     SET _parent=
REM     DEL "%_jsonxreferences%" 2>NUL
REM )
SHIFT
GOTO MAIN


REM        ------------------------------
REM  3 --> Update ripped discs dashboard.
REM        ------------------------------
:STEP3
SET _path=%PATH%
SET path=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
PUSHD %_grabber%
python RippedDiscs.py
POPD
SET path=%_path%
SET _path=
SHIFT
GOTO MAIN


REM        ----------------------------
REM  4 --> Prepare NAS Syncing. Step 2.
REM        ----------------------------
:STEP4
REM IF EXIST %_txtfiles% (
REM     PUSHD %_grabber%
REM     python RippedTracks2NAS.py
REM     POPD
REM )
SHIFT
GOTO MAIN


REM        --------------
REM  5 --> Miscellaneous.
REM        --------------
:STEP5
PUSHD %TEMP%
DEL sequences.json 2> NUL
POPD
SHIFT
GOTO MAIN


REM        ------------
REM  6 --> Exit script.
REM        ------------
:THE_END
IF DEFINED _mycp CHCP %_mycp% > NUL
SET _chcp=
SET _cp=
SET _errorlevel=
SET _grabber=
SET _jsontags=
SET _jsonxreferences=
SET _me=
SET _mycp=
SET _myparent=
SET _path=
SET _txtfiles=
ENDLOCAL
EXIT /B %_errorlevel%
