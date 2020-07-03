@ECHO off
@CLS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM    ==================
REM A. Initializations 1.
REM    ==================
SET _me=%~n0
SET _myparent=%~dp0


REM    ==================
REM B. Initializations 2.
REM    ==================
SET _tempdir=
SET _cp=1252
SET _ok=0
SET _index=0
SET _errorlevel=0
SET _xxcopy=xxcopy.cmd


REM    ==================
REM C. Initializations 3.
REM    ==================
SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent%Resources


REM     =====================================================
REM  D. Allow interface to decode Latin-1 encoded characters.
REM     =====================================================

REM Set code page.
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp (
    IF NOT DEFINED _mycp SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

REM Get code page.
SET _step=1
CALL shared.cmd
@IF DEFINED _chcp ECHO Le code page est %_chcp%.

REM Check characters encoding.
@ECHO Les caractères accentués sont restitués proprement ^^!
FOR /F "usebackq tokens=*" %%A IN ("accentuated.txt") DO ECHO %%A


REM    ===============
REM E. Check argument.
REM    ===============
:ARGUMENT
IF "%~1" EQU "P" SET _ok=1
IF "%~1" EQU "T" SET _ok=1
IF %_ok% EQU 0 (
    ECHO:
    ECHO:
    ECHO Argument erroné reçu par le script ^^! Doit être [P]roduction ou [T]est. %~1 a été reçu.
    IF DEFINED _mycp (
        CHCP %_mycp% > NUL
        ECHO:
        ECHO:
        ECHO Le code page est maintenant %_mycp%.
    )
    PAUSE
    POPD
    ENDLOCAL
    EXIT /B 0
)


:MAIN
PUSHD ..\MyPythonProject


REM    =============================
REM F. Create temporary environment.
REM    =============================
FOR /F "usebackq tokens=*" %%A IN (`python temporaryenv.py dir -f`) DO (
    IF !_index! EQU 0 (
        SET _tempdir=%%A
        SET _parent=%%~dpA
        SET _name=%%~nA
    )
    IF !_index! EQU 1 SET _tempfil=%%A
    SET /A "_index+=1"
)
(
    ECHO L'environnement de travail est %_tempdir%.
    ECHO:
    ECHO:
    PAUSE
    CLS
)


REM    ==========
REM G. Java step.
REM    ==========
REM    Enumerate files.
PUSHD ..\MyJavaProject\out\production\MyJavaProject
java com.xavier.computing.Finder "F:" "999999999" "PRODUCTION" --regex "^.+\.(m4a|mp3)" --output %_tempfil% > NUL
POPD


REM    ============
REM H. Python step.
REM    ============
REM    Process files.
PUSHD Backup
python lossy.py "%_tempfil%" "%_tempdir%\%_xxcopy%"
POPD
PUSHD %_tempdir%
IF EXIST %_xxcopy% (
    CLS
    ECHO:
    CHOICE /C ON /T 30 /N /D N /M "Le fichier de commandes a été créé avec succès. Voulez-vous consulter son contenu ? Presser [O] pour Oui ou [N] pour Non. "
    IF NOT ERRORLEVEL 2 (
        CLS
        ECHO:
        TYPE %_xxcopy%
        ECHO:
        ECHO:
        PAUSE
    )
)
POPD


REM    ==================
REM I. Run commands file.
REM    ==================
IF "%~1" EQU "P" (
    PUSHD %_tempdir%
    CALL %_xxcopy% 0
    POPD
)


REM    ============
REM J. Exit script.
REM    ============
:THE_END

REM -----
IF "%~1" EQU "P" IF DEFINED _parent IF EXIST %_parent% (
    PUSHD %_parent:~0,-1%
    RMDIR %_name% /S /Q 2> NUL
    POPD
    IF NOT EXIST %_name% ECHO "%_tempdir%" a été supprimé avec succès ^^!
)

REM -----
@IF DEFINED _mycp (
    CHCP %_mycp% > NUL
    ECHO:
    ECHO:
    ECHO Le code page est maintenant %_mycp%.
    ECHO:
    ECHO:
    PAUSE
)

REM -----
POPD
POPD
PAUSE
CLS
(
    ENDLOCAL
    EXIT /B %_errorlevel%
)
