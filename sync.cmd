@ECHO off

@REM Exécuter les commandes ROBOCOPY configurées dans le fichier "E:\Computing\sync.ini".

CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


@REM ================
@REM Initialisations.
@REM ================
SET _cp=65001
SET _first=1
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
IF DEFINED _chcp IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
IF NOT EXIST "%~1" GOTO END


@REM =================
@REM Script principal.
@REM =================
FOR /F "usebackq eol=# tokens=1,2 delims=" %%I IN ("%~1") DO (
    SET _key=
    SET _value=
    SET _batch=1
    FOR /F "usebackq tokens=1,2 delims==" %%A IN ('%%~I') DO IF [%%B] NEQ [] (
        SET _batch=0
        SET _key=%%~A
        SET _value=%%~B
    )


    @REM    -------------------------------
    @REM A. Un bloc commande est rencontré.
    @REM    -------------------------------
    @REM    La commande construite précédemment est exécutée.
    @REM    Une nouvelle commande est ensuite initialisée.
    IF [!_batch!] EQU [1] (
        IF [!_first!] EQU [0] IF [!_src!!_dst!] EQU [11] CALL :RUN "!_string!"
        SET _xd=
        SET _xf=
        SET _src=0
        SET _dst=0
        SET _string=ROBOCOPY
    )


    @REM    ---------------------------------
    @REM B. Un bloc clé/valeur est rencontré.
    @REM    ---------------------------------
    @REM    La valeur est insérée dans la commande.
    IF [!_batch!] EQU [0] (

        CALL :TOKENIZE "!_string!" _base _xd_option _xf_option

        @REM La clé est "src" ou "dst".
        IF [!_key!] EQU [src] IF [!_src!!_dst!] EQU [00] SET _base=!_base! "!_value!"&& SET _src=1
        IF [!_key!] EQU [dst] IF [!_src!!_dst!] EQU [10] SET _base=!_base! "!_value!"&& SET _dst=1
        IF [!_key!] EQU [dst] IF [!_src!!_dst!] EQU [00] SET _base=!_base! "!_value!"&& SET _dst=1
        IF [!_key!] EQU [src] IF [!_src!!_dst!] EQU [01] FOR /F "usebackq tokens=1,2" %%X IN ('!_base!') DO SET _base=%%X "!_value!" %%Y&& SET _src=1

        @REM La clé est "xd" : un répertoire est exclus de la copie.
        IF [!_key!] EQU [xd] (
            IF NOT DEFINED _xd_option SET _xd=/XD
            SET _xd=!_xd! "!_value!"
        )

        @REM La clé est "xf" : un fichier est exclus de la copie.
        IF [!_key!] EQU [xf] (
            IF NOT DEFINED _xf_option SET _xf=/XF
            SET _xf=!_xf! "!_value!"
        )

        @REM Les différentes portions constituant la commande sont assemblées.
        SET _string=!_base!
        IF DEFINED _xd SET _string=!_string! !_xd!
        IF DEFINED _xf SET _string=!_string! !_xf!

    )
    SET _first=0

)

@REM La dernière commande assemblée est exécutée avant achèvement du script.
IF [%_src%%_dst%] EQU [11] CALL :RUN "%_string%"
SET _cp=
SET _xd=
SET _xf=
SET _dst=
SET _src=
SET _batch=
SET _first=
SET _string=
ENDLOCAL
EXIT /B 0


@REM ================
@REM Local functions.
@REM ================
:RUN
SETLOCAL ENABLEEXTENSIONS
SET _ok=1
SET _command=
FOR /F "usebackq tokens=1-3,*" %%A IN ('%~1') DO (
    IF [%%A] NEQ [ROBOCOPY] SET _ok=0
    IF [%%B] EQU [] SET _ok=0
    IF [%%C] EQU [] SET _ok=0
)
IF [%_ok%] EQU [0] GOTO ABORT
FOR /F "usebackq tokens=1-3,*" %%A IN ('%~1') DO SET _command=%%A %%B %%C /MIR %%D
@ECHO:
@ECHO:
@ECHO La commande suivante va être exécutée :
@ECHO %_command%
CHOICE /C ON /CS /T 30 /d N /N /m "Voulez-vous exécuter cette commande [O/N] ? "
IF %ERRORLEVEL% EQU 1 %_command%
:ABORT
(
    SET _command=
    ENDLOCAL
)
EXIT /B 0


:TOKENIZE
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _base=
SET _xd_option=
SET _xf_option=
FOR /F "usebackq tokens=1-3 delims=/" %%A IN ('%~1') DO (
    IF [%%C] NEQ [] (
        SET _token=%%C
        SET _token=!_token:~0,2!
        IF "!_token!" EQU "XD" FOR /F "usebackq tokens=1,*" %%X IN ('%%C') DO SET _xd_option=%%Y
        IF "!_token!" EQU "XF" FOR /F "usebackq tokens=1,*" %%X IN ('%%C') DO SET _xf_option=%%Y
    )
    IF [%%B] NEQ [] (
        SET _token=%%B
        SET _token=!_token:~0,2!
        IF "!_token!" EQU "XD" FOR /F "usebackq tokens=1,*" %%X IN ('%%B') DO SET _xd_option=%%Y
        IF "!_token!" EQU "XF" FOR /F "usebackq tokens=1,*" %%X IN ('%%B') DO SET _xf_option=%%Y
    )
    SET _base=%%A
)
(
    SET _base=
    SET _token=
    SET _xd_option=
    SET _xf_option=
    ENDLOCAL
    SET %2=%_base%
    SET %3=%_xd_option%
    SET %4=%_xf_option%
)
EXIT /B 0
