@ECHO off
REM  1. Exécuté depuis le scheduler windows : "G:\Computing\start.cmd" 1 3 4 6 7 9 10 11 13.
REM  2. Exécuté manuellement : "G:\Computing\start.cmd" 16 I 17 J
REM  3. Exécuté manuellement : "G:\Computing\start.cmd" 21 "2007"
REM  4. Exécuté manuellement : "G:\Computing\start.cmd" 16 I 17 J 21 "2012" 21 "2013"


REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _videos=%USERPROFILE%\videos
SET _log=%_COMPUTING%\XXCOPYFilesLog.log


REM ===============
REM Main algorithm.
REM ===============


REM     ------
REM  2. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "6" GOTO STEP6
IF "%~1" EQU "7" GOTO STEP7
IF "%~1" EQU "9" GOTO STEP9
IF "%~1" EQU "10" GOTO STEP10
IF "%~1" EQU "11" GOTO STEP11
IF "%~1" EQU "12" GOTO STEP12
IF "%~1" EQU "13" GOTO STEP13
IF "%~1" EQU "14" GOTO STEP14
IF "%~1" EQU "15" GOTO STEP15

REM Sync mobile media (mobile phone, car SD Card, car USB drive, etc). Both audio and videos.
REM Use the right argument depending on the source drive.
IF "%~1" EQU "16" (
    SET repository1=G:\Music\MP3\
    SET repository2=%_COMPUTING%\Arguments.xav
    SET exceptions=%_COMPUTING%\Exceptions.xav
    SET filters=*\*.mp3
    SET drive=%~2
    SHIFT
    GOTO STEP16
)

REM Sync FIIO X5 lossless music player. Audio only!
REM Use the right argument depending on the source drive.
IF "%~1" EQU "17" (
    SET repository1=G:\Music\FLAC\
    SET repository2=
    SET exceptions=
    SET filters=
    SET drive=%~2
    SHIFT
    GOTO STEP16
)

REM Sync mobile media (mobile phone, car SD Card, car USB drive, etc). Audio only!
REM Use the right argument depending on the source drive.
IF "%~1" EQU "18" (
    SET repository1=G:\Music\MP3\
    SET repository2=
    SET exceptions=
    SET filters=*\*.mp3
    SET drive=%~2
    SHIFT
    GOTO STEP16
)

REM Backup Bruce Springsteen lossless audio files.
REM Require two mandatory arguments: both "21" and a year composed of four digits.
IF "%~1" EQU "19" (
    SET drive=F
    SET src=!drive!:\*\Springsteen*\*\%~2\*\*.flac
    SHIFT
    GOTO STEP15
)

REM Copy media files from logical repository.
IF "%~1" EQU "20" (
    SET dst=%~2
    SET repository=%~3
    SHIFT
    SHIFT
    GOTO STEP17
)

SHIFT
GOTO MAIN


REM     --------------------------
REM  3. Clear temporary directory.
REM     --------------------------
REM     /DB#1: REMoves files older than or equal to 1 day.
:STEP1
XXCOPY %TEMP%\ /RS /DB#1 /R /H /Y /PD0 /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------------------------------------
REM  5. Backup "sandboxie.ini" and others single important files.
REM     ---------------------------------------------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incREMentally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    XXCOPY "%WINDIR%\sandboxie.ini" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.gnucash" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.xlsx" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\database.db" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\logging.yml" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\.gitignore" "y:\" /KS /Y /BI /FF
)
SHIFT
GOTO MAIN

REM     -----------------------
REM  6. Remove Areca log files.
REM     -----------------------
REM     /DB#8: REMoves files older than or equal to 8 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\*.log /RS /DB#8 /R /H /Y /PD0 /ED /Fo:%_log% /FM:DTL
SHIFT
GOTO MAIN


REM     ---------------------------------
REM  8. Backup "mypythonproject" content.
REM     ---------------------------------
REM     /DB#10: REMoves files older than or equal to 10 days.
REM     /IA   : copies file(s) only if destination directory doesn't exist.
:STEP6
IF EXIST y:\python (
    XXCOPY y:\python\ /S /RS /FC /DB#10 /R /H /Y /PD0 /Fo:%_log% /FM:DTL
    XXCOPY %_PYTHONPROJECT%\*\ y:\python\/$ymmdd$\ /X:*.pyc /X:*.xml /IA /KS /BI /FF /Y /R /Fo:%_log% /FM:DTL /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM  9. Backup both CSS ans XSL sheets.
REM     -------------------------------
REm     /SX: flattens subdirectories.
:STEP7
IF EXIST "y:" (
    XXCOPY %_COMPUTING%\*.css y:\ /SX /KS /Y /BI /FF
    XXCOPY %_COMPUTING%\*.js  y:\ /SX /KS /Y /BI /FF
    XXCOPY %_COMPUTING%\*.xsl y:\ /SX /KS /Y /BI /FF
)
SHIFT
GOTO MAIN


REM     ---------------------
REM 10. Backup PDF documents.
REM     ---------------------
:STEP9
IF EXIST "z:\Z123456789" XXCOPY "%_MYDOCUMENTS%\Administratif\*\*.pdf" "z:\Z123456789\" /KS /BI /FF /Y /R /Fo:%_log% /FM:DTL /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -----------------
REM 11. Clone album arts.
REM     -----------------
:STEP10
IF EXIST "z:\Z123456790" XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" "z:\Z123456790\" /CLONE /Fo:%_log% /FM:DTL /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------
REM 12. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF EXIST "z:\Z123456791" XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /X:*.log /X:*.zip /CLONE /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------
REM 13. Clone videos.
REM     -------------
:STEP12
IF EXIST "z:\Z123456792" XXCOPY "%_videos%\*.mp4" "z:\Z123456792\" /CLONE /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------
REM 14. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
python G:\Computing\MyPythonProject\Tasks\Task01.py
SHIFT
GOTO MAIN


REM     ---------------------------------------
REM 15. Clone "H:" to "\\Diskstation\pictures".
REM     ---------------------------------------
:STEP14

REM -->  1. Clone "H:" to "\\Diskstation\pictures". Don't delete extra files.
REM         Exclude "RECYCLER".
REM         Exclude "$RECYCLE.BIN".
REM         Exclude "SYSTEM VOLUME INFORMATION".
REM         Exclude "IPHONE".
REM         Exclude "RECOVER".
XXCOPY "H:\*\*.jpg" "\\Diskstation\pictures\" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /CLONE /Z0 /oA:%_XXCOPYLOG%

REM -->  2. Reverse both source and destination. Then REMove brand new files but exclude "#recycle" folder.
REM         This trick allows to REMove files from "\\Diskstation\pictures" not present in "H:". And preserve "#recycle"!
XXCOPY "\\Diskstation\pictures\" "H:\" /RS /BB /S /PD0 /RSY /X:#recycle\ /oA:%_XXCOPYLOG% /Fo:%_log% /FM:DTL

SHIFT
GOTO MAIN


REM     ------------------------------------
REM 16. Clone "F:" to "\\Diskstation\music".
REM     ------------------------------------
REM     Only FLAC.
:STEP15
ECHO XXCOPY "%src%" "\\Diskstation\music\" /X:*recycle*\ /X:*volume*\ /KS /S /R /Q /Y /BI /FF /oA:%_XXCOPYLOG% /Fo:%_log% /FM:DTL
ECHO XXCOPY "\\Diskstation\music\" "%drive%:\" /RS /BB /S /PD0 /RSY /X:#recycle\ /oA:%_XXCOPYLOG% /Fo:%_log% /FM:DTL
SHIFT
GOTO MAIN


REM     ------------------
REM 17. Sync mobile media.
REM     ------------------
:STEP16

REM -->  0. Clear screen.
CLS

REM -->  1. Sauvegarde des répertoires ne devant pas être définitivement supprimés.
IF DEFINED exceptions (
    IF EXIST "!exceptions!" (
        FOR /F "usebackq eol=# tokens=*" %%i IN ("!exceptions!") DO (
            IF EXIST "%TEMP%\%%~i" (
                RMDIR /S /Q "%TEMP%\%%~i"
            )
            XXCOPY "%drive%:\%%~i\" "%TEMP%\%%~i\" /S /oA:%_XXCOPYLOG%
        )
    )
)

REM -->  2. Copie des fichiers composant le premier repository.
REM         Repository physique.
IF DEFINED repository1 (
    IF EXIST "!repository1!" (
        SET repository=!repository1!\
        IF DEFINED filters (
            SET repository=!repository1!\!filters!
        )
        XXCOPY "!repository!" "%drive%:\" /CLONE /PZ0 /FF /oA:%_XXCOPYLOG%
    )
)

REM -->  3. Copie des fichiers composant le deuxième repository.
REM         Repository logique.
IF DEFINED repository2 (
    IF EXIST !repository2! (
        FOR /F "usebackq eol=# tokens=*" %%i IN ("!repository2!") DO (
            XXCOPY "%%~i" "%drive%:\" /oA:%_XXCOPYLOG%
        )
    )
)

REM -->  4. Restauration des répertoires ne devant pas être définitivement supprimés.
IF DEFINED exceptions (
    IF EXIST "!exceptions!" (
        FOR /F "usebackq eol=# tokens=*" %%i IN ("!exceptions!") DO (
            XXCOPY "%TEMP%\%%~i\" "%drive%:\%%~i\" /S /oA:%_XXCOPYLOG%
        )
    )
)

SHIFT
GOTO MAIN


REM     -----------------------------------------
REM 18. Copy media files from logical repository.
REM     -----------------------------------------
:STEP17
CLS
IF EXIST "%repository%" (
    FOR /F "usebackq eol=# tokens=*" %%i IN ("%repository%") DO (
        XXCOPY "%%~i" "%dst%\" /oA:%_XXCOPYLOG%
    )
)
SHIFT
GOTO MAIN
