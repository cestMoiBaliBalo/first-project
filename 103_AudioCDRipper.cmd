@ECHO off
REM Stocker dans un fichier JSON les arguments permettant de copier un fichier audio FLAC
REM Le nom du fichier audio est re�u en qualit� de premier param�tre.
REM Le nom du fichier audio est transmis en qualit� de premier param�tre.
REM La lettre identifiant le lecteur re�evant le fichier copi� est transmise en qualit� de deuxi�me param�tre.
REM Le nom du fichier JSON est transmis en qualit� de troisi�me param�tre.


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
REM Enum�rer les lecteurs disponibles.
REM ==================================
REM wscript "G:\Computing\Serial.vbs"


REM ======================================================================
REM D�tecter le lecteur amovible poss�dant le num�ro de s�rie "962933300".
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
REM PUSHD %_PYTHONPROJECT%
REM python AudioCD\DigitalAudioFiles`CopyArguments.py "%~1" "%_drive%:"
REM POPD
