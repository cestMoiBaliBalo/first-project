@ECHO off
REM  1. Exécuté depuis le scheduler windows : "G:\Computing\start.cmd" 1 3 4 6 7 9 10 11 13.
REM  2. Exécuté manuellement : "G:\Computing\start.cmd" 16 I 17 J


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
SET _areca=C:/Program Files/Areca/areca_cl.exe
SET _lossless=G:\Music\Lossless
SET _lossy=G:\Music\Lossy
SET _videos=%USERPROFILE%\videos
SET _exclusions1=G:\Computing\Resources\exclusions1.txt


REM ===============
REM Main algorithm.
REM ===============
CHCP 1252


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
IF "%~1" EQU "18" GOTO STEP18
IF "%~1" EQU "19" GOTO STEP19
IF "%~1" EQU "20" GOTO STEP20
IF "%~1" EQU "21" GOTO STEP21
IF "%~1" EQU "22" GOTO STEP22
IF "%~1" EQU "24" GOTO STEP24
IF "%~1" EQU "25" GOTO STEP25

SHIFT
GOTO MAIN


REM     --------------------------
REM  3. Clear temporary directory.
REM     --------------------------
REM     /DB#1 Removes files older than or equal to 1 day.
REM     /RS   Removes files in the source (the only) directory.
REM     /S    Processes directories and subdirectories except empty ones.
REM     /R    Deletes even a read-only file.
REM     /H    Deletes even a hidden/system file.
REM     /PD0  Suppresses the prompt which would appear on a directory.
REM     /Y    Suppresses the prompt prior to each file-delete.
REM     /ED   Preserves the directory even if it becomes empty.
REM     /ED1  Preserves 1 level of empty directories. All subdirectories under %TEMP% are removed.
:STEP1
XXCOPY %TEMP%\ /RS /S /DB#1 /R /H /Y /PD0 /ED1 /X:*.lst /oA:%_XXCOPYLOG%
XXCOPY C:\Users\Xavier\AppData\Local\*.txt /RS /DB#1 /R /H /Y /PD0 /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------------------------------------
REM  5. Backup "sandboxie.ini" and others single important files.
REM     ---------------------------------------------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    XXCOPY "%WINDIR%\sandboxie.ini" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.gnucash" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.xlsx" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\Database.kdbx" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\Resources\database.db" "y:\" /KS /Y /BI /FF
)
SHIFT
GOTO MAIN


REM     -----------------------
REM  6. Remove Areca log files.
REM     -----------------------
REM     /DB#14: removes files older than or equal to 14 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\*.log /RS /DB#14 /R /H /Y /PD0 /ED
SHIFT
GOTO MAIN


REM     ------------------------------
REM  8. Backup "G:\Computing" content.
REM     ------------------------------
REM     /DB#14: removes files older than or equal to 14 days.
REM     /IA   : copies file(s) only if destination directory doesn't exist.
:STEP6
IF EXIST y:\Computing XXCOPY y:\Computing\ /S /RS /FC /DB#14 /R /H /Y /PD0
XXCOPY %_COMPUTING%\ y:\Computing\/$ymmdd$\ /S /EX:"%_exclusions1%" /IA /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------------------------------------------------
REM  9. Clone "\\Diskstation\backup\Images\Samsung S5" to "G:\Videos\Samsung S5".
REM     -------------------------------------------------------------------------
REM     Extra files are deleted.
:STEP7
XXCOPY "\\Diskstation\backup\Images\Samsung S5\" "G:\Videos\Samsung S5\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     --------------------
REM 10. Clone PDF documents.
REM     --------------------
:STEP9
IF EXIST "z:\Z123456789" XXCOPY "%_MYDOCUMENTS%\Administratif\*\*.pdf" "z:\Z123456789\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
IF EXIST "%_CLOUDSTATION%\Documents\Administratif" XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "%_CLOUDSTATION%\Documents\Administratif\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
IF [%2] EQU [] (
    ECHO:
    ECHO:
    PAUSE
)
SHIFT
GOTO MAIN


REM     -----------------
REM 11. Clone album arts.
REM     -----------------
:STEP10
IF EXIST "z:\Z123456790" XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" "z:\Z123456790\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------
REM 12. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF EXIST "z:\Z123456791" XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /X:*.log /X:*.zip /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -----------------
REM 13. Clone MP4 videos.
REM     -----------------
:STEP12
IF EXIST "z:\Z123456792" XXCOPY "%_CLOUDSTATION%\Vidéos\*.mp4" "z:\Z123456792\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------
REM 14. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
python G:\Computing\MyPythonProject\Tasks\Task01.py
SHIFT
GOTO MAIN


REM     ------------------------------------------------
REM 15. Clone "\\Diskstation\Images\Collection" to "H:".
REM     ------------------------------------------------
::STEP14

:: -->  1. Clone "\\Diskstation\Images\Collection" to "H:". Don't delete extra files and directories!
::XXCOPY "\\Diskstation\backup\Images\Collection\" "H:\" /CLONE /Z0 /oA:%_XXCOPYLOG%

:: -->  2. Reverse both source and destination. Then remove brand new files but preserve:
::         - "RECYCLER".
::         - "$RECYCLE.BIN".
::         - "SYSTEM VOLUME INFORMATION".
::         - "IPHONE".
::         - "RECOVER".
::XXCOPY "H:\" "\\Diskstation\backup\Images\Collection\" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%

::SHIFT
::GOTO MAIN


REM     -----------------------------------------------
REM 16. Copy audio FLAC files to "\\Diskstation\music".
REM     -----------------------------------------------
:STEP20
XXCOPY "F:\%~2\?*\2\%~3\*\*.flac" "\\Diskstation\music\%~2\" /KS /BI /FF /I /Y /oA:%_XXCOPYLOG%
XXCOPY /CE "\\Diskstation\music\" "F:\" /X:*recycle\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%
SHIFT
SHIFT
SHIFT
GOTO MAIN


REM     -----------------
REM 19. Backup documents.
REM     -----------------
:STEP18
IF EXIST "y:" (
    REM Incremental backup.
    REM Target Group : "workspace.documents".
    REM Target : "Documents (USB Drive)".
    "%_areca%" backup -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg"
    python -m Applications.Database.Tables.shared select 123456802 --days 20
    IF ERRORLEVEL 1 (
        "%_areca%" merge -c -k -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg" -from 0 -to 0
        python -m Applications.Database.Tables.shared update 123456802
    )
)
IF [%2] EQU [] (
    ECHO:
    ECHO:
    PAUSE
)
SHIFT
GOTO MAIN


REM     ----------------------------------
REM 19. Move videos to local CloudStation.
REM     ----------------------------------
:STEP19
python -m Applications.Database.Tables.shared select 123456801 --days 5
IF ERRORLEVEL 1 (
    python G:\Computing\MyPythonProject\Tasks\Task04.py
    IF ERRORLEVEL 0 (
        python -m Applications.Database.Tables.shared update 123456801
    )
)
SHIFT
GOTO MAIN


REM     ----------------------------
REM 21. Backup AVCHD videos to "X:".
REM     ----------------------------
:STEP24
SHIFT
GOTO MAIN
XXCOPY "G:\Videos\AVCHD Videos\" "X:\Repository\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN
