@ECHO off
SETLOCAL ENABLEDELAYEDEXPANSION


REM On a un fichier texte en UTF-16 tel que produit par dBpoweramp.
REM On lance le script python `ripper.py` tel que appelé par dBpoweramp également.
REM Il produit les tags et les fichiers JSON pour la base de données Audio.
REM On lance ensuite `ripper.cmd` tel que appelé par dBpoweramp.
REM On peut alors utiliser le module unittest pour contrôler que l'enregistrement le plus récent dans la table `rippinglog` correspond
REM bien aux données du fichier texte en entrée.
REM On peut également comparer les tags du fichier produit dans %TEMP% et les tags auxquels on s'attend.


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _jsonrippedcd=%TEMP%\rippinglog.json
SET _jsonrippedtracks=%TEMP%\digitalaudiodatabase.json


REM ===============
REM Main algorithm.
REM ===============
CHCP 1252


REM    ------------
REM A. Choose test.
REM    ------------
CLS
ECHO:
ECHO:
ECHO: A. Single disc (default^).
ECHO: B. Multi discs.
ECHO: C. All tests.
ECHO: Q. Quit.
ECHO:
ECHO:
CHOICE /C ABCQ /T 10 /N /D Q /M "Please choose test:"
IF ERRORLEVEL 4 GOTO FIN
IF ERRORLEVEL 3 GOTO FIN
IF ERRORLEVEL 2 GOTO FIN
IF ERRORLEVEL 1 SET _command="Ripper.py" "%_COMPUTING%\Resources\CDRipper_default.txt" "default" --test


REM    ------------------
REM B. Choose debug mode.
REM    ------------------
CLS
ECHO:
ECHO:
CHOICE /C YN /T 10 /N /D N /M "Would you like to set DEBUG mode? Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 GOTO STEP1
IF ERRORLEVEL 1 SET _command=%_command% --debug


REM    ----------------
REM C. Run `ripper.py`.
REM    ----------------
CLS
ECHO:
ECHO:
ECHO: STEP 1: Run `ripper.py`.
PUSHD %_PYTHONPROJECT%\AudioCD
python %_command%
IF ERRORLEVEL 100 (
    ECHO:
    ECHO:
    ECHO: An error occured into `Ripper.py`. Enable DEBUG mode and see python log for further details.
    ECHO:
    PAUSE
    POPD
    GOTO FIN
)
POPD
ECHO:
ECHO:
ECHO:No error detected. Script will continue.& PAUSE


REM    -------------------
REM D. Sync test database.
REM    -------------------
SET _file=0
IF EXIST "%_jsonrippedcd%" SET _file=1
IF EXIST "%_jsonrippedtracks%" SET _file=1
IF %_file% EQU 1 (
    CLS
    ECHO:
    ECHO:
    ECHO: STEP 2: Sync test database.
    XXCOPY "G:\Computing\Resources\database.db" "G:\Computing\MyPythonProject\Applications\Tests\" /BI /FF /Y /oA:%_XXCOPYLOG% >NUL 2>&1
    ECHO:
    ECHO:
    ECHO:Script will continue.& PAUSE
)


REM    ----------------
REM E. Run `ripper.py`.
REM    ----------------
SET _errorlevel=0
IF EXIST "%_jsonrippedcd%" (
    CLS
    ECHO:
    ECHO:
    ECHO: STEP 3: Run `ripper.cmd`.
    PUSHD %_COMPUTING%
    CALL "ripper.cmd" 1
    SET _errorlevel=!ERRORLEVEL!
    POPD
    ECHO:
    ECHO:
    ECHO:!_errorlevel! record(s^) inserted into `rippinglog` table. Script will continue.& PAUSE
)


REM    ----------------------------
REM F. Run unittest python modules.
REM    ----------------------------
IF %_errorlevel% GTR 0 (
    CLS
    ECHO:
    ECHO:
    ECHO: STEP 4: Run unittest python modules.
    ECHO:
    ECHO:
    python -m unittest Applications.Tests.ripper.Test01DefaultCDTrack >NUL 2>&1
    SET _errorlevel=!ERRORLEVEL!
    IF !_errorlevel! EQU 0 ECHO:All tests succeeded.& PAUSE
    IF !_errorlevel! GTR 0 ECHO:At least one test failed.& PAUSE
)


:FIN
EXIT /B 0
