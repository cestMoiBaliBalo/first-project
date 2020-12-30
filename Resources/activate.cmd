@ECHO off
@CLS
@SET _cp=1252
@SET _mycp=

@REM L'argument reçu est le nom de l'environnement virtuel à mettre en place.
IF NOT EXIST "%_PYTHONPROJECT%\VirtualEnv\%~1" EXIT /B 0

@REM Permettre à la console de restituer les caractères accentué.
@FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
@IF DEFINED _chcp (
    @SET _mycp=%_chcp%
    IF NOT [%_chcp%]==[%_cp%] CHCP %_cp% > NUL
)

@REM Mettre en place l'environnement virtuel.
SET "VIRTUAL_ENV=%_PYTHONPROJECT%\VirtualEnv\%~1"
IF NOT DEFINED _prompt SET _prompt=$P$G
IF DEFINED _OLD_VIRTUAL_PROMPT SET _prompt=%_OLD_VIRTUAL_PROMPT%
IF DEFINED _OLD_VIRTUAL_PYTHONHOME SET "PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%"
SET _OLD_VIRTUAL_PROMPT=%_prompt%
SET _prompt=(%~1) %_prompt%
IF DEFINED PYTHONHOME (
    SET _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
    SET PYTHONHOME=
)
IF DEFINED _OLD_VIRTUAL_PATH SET "PATH=%_OLD_VIRTUAL_PATH%"
IF NOT DEFINED _OLD_VIRTUAL_PATH SET "_OLD_VIRTUAL_PATH=%PATH%"
SET "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

@REM Mettre en place la nouvelle invite de commande.
PROMPT %_prompt%
EXIT /B 0
