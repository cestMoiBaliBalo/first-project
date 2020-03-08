REM @ECHO off


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
SET _errorlevel=0
SET _grabber=%_PYTHONPROJECT%\AudioCD\Grabber
SET _jsontags=%TEMP%\tags.json
SET _jsonxreferences=%TEMP%\xreferences.json
SET _txtfiles=%_RESOURCES%\rippedtracks.txt


REM ============
REM Main script.
REM ============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


:MAIN
IF "%~1" EQU "" (
    SET _cp=
    SET _errorlevel=
    SET _grabber=
    SET _jsontags=
    SET _jsonxreferences=
    SET _txtfiles=
    SET _me=
    SET _myparent=
    ENDLOCAL
    EXIT /B %_errorlevel%
)
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
    FOR /F %%I IN ("%_grabber%") DO SET _parent=%%~dpI
    PUSHD !_parent!
    python Insert_Albums.py "%_jsontags%"
    POPD
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
PUSHD %_grabber%
python RippedDiscs.py
POPD
SHIFT
GOTO MAIN


REM        ----------------------------
REM  4 --> Prepare NAS Syncing. Step 2.
REM        ----------------------------
:STEP4
IF EXIST %_txtfiles% (
    PUSHD %_grabber%
    python RippedTracks2NAS.py
    POPD
)
SHIFT
GOTO MAIN


:STEP5
PUSHD %TEMP%
DEL sequences.json 2> NUL
POPD
SHIFT
GOTO MAIN
