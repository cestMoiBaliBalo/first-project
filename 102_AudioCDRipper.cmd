@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM =====================================================================
REM Exécuter les copies énumérées dans le fichier JSON reçu en paramètre.
REM =====================================================================
IF EXIST "%~1" (
    PUSHD "%_PYTHONPROJECT%"
    IF "%~2" NEQ "" (
        python AudioCD\DigitalAudioFiles`Copy.py "%~1" -d %~2
    ) ELSE (
        python AudioCD\DigitalAudioFiles`Copy.py "%~1"
    )
    POPD
    DEL "%~1"
)
