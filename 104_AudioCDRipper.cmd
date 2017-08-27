@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initialisations 2.
REM ==================
SET _drives=%TEMP%\serial.txt


REM ==================================
REM Enumérer les lecteurs disponibles.
REM ==================================
wscript "G:\Computing\Serial.vbs"


REM ======================================================================
REM Détecter le lecteur amovible possédant le numéro de série "962933300".
REM ======================================================================
IF NOT EXIST "%_drives%" EXIT /B 100
IF EXIST "%_drives%" (
    FOR /F "delims=; tokens=1-2 usebackq" %%a IN ("%_drives%") DO (
        IF "%%b" == "962933300" (
            SET _drive=%%a
        )
    )
)
IF NOT DEFINED _drive EXIT /B 100


REM ======================================================
REM Ecrire les arguments de copie dans un un fichier JSON.
REM ======================================================
PUSHD %_PYTHONPROJECT%
IF "%~1" NEQ "" (
    python AudioCD\DigitalAudioFiles`UpdateTags.py "%_drive%:" -d %~1
) ELSE (
    python AudioCD\DigitalAudioFiles`UpdateTags.py "%_drive%:"
)
POPD
