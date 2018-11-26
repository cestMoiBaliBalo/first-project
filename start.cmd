@ECHO off


REM  1. Exécuté depuis le scheduler windows : "G:\Computing\start.cmd" 1 3 4 6 7 9 10 11 13.
REM  2. Exécuté manuellement : "G:\Computing\start.cmd" 16 I 17 J


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
SET _areca=C:/Program Files/Areca/areca_cl.exe
SET _cp=1252
SET _exclusions1=G:\Computing\Resources\exclusions1.txt
SET _lossless=G:\Music\Lossless
SET _lossy=G:\Music\Lossy
SET _sdcard=%_COMPUTING%\Resources\SDCard-content.txt
SET _videos=%USERPROFILE%\videos


REM ===============
REM Main algorithm.
REM ===============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp%


REM     ------
REM  2. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" (
    PAUSE
    EXIT /B %ERRORLEVEL%
)
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
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
XXCOPY %TEMP%\ /RS /S /DB#1 /R /H /Y /PD0 /ED1 /oA:%_XXCOPYLOG%
XXCOPY C:\Users\Xavier\AppData\Local\*.txt /RS /DB#1 /R /H /Y /PD0 /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ------------------------------
REM  4. Backup single important files.
REM     ------------------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    SET _first=1
    FOR /F "usebackq delims=| tokens=1,2" %%F IN ("%_sdcard%") DO (
        IF ["%%~G"] EQU [""] (
            SET _switch=/CE
            IF !_first! EQU 1 SET _switch=/EC
            SET _first=0
            CALL SET _file=%%~F
            XXCOPY !_switch! "!_file!" "y:\" /KS /Y /BI /FF /oA:%_XXCOPYLOG%
        )
    )
)
SHIFT
GOTO MAIN


REM     -----------------------
REM  5. Remove Areca log files.
REM     -----------------------
REM     /DB#14: removes files older than or equal to 14 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\*.log /RS /DB#14 /R /H /Y /PD0 /ED
SHIFT
GOTO MAIN


REM     ------------------------------
REM  6. Backup "G:\Computing" content.
REM     ------------------------------
REM     /DB#14: removes files older than or equal to 14 days.
REM     /IA   : copies file(s) only if destination directory doesn't exist.
:STEP6
IF EXIST y:\Computing XXCOPY y:\Computing\ /S /RS /FC /DB#14 /R /H /Y /PD0
XXCOPY %_COMPUTING%\ y:\Computing\/$ymmdd$\ /S /EX:"%_exclusions1%" /IA /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------------------------------------------------
REM  7. Clone "\\Diskstation\backup\Images\Samsung S5" to "G:\Videos\Samsung S5".
REM     -------------------------------------------------------------------------
REM     Extra files are deleted.
:STEP7
XXCOPY "\\Diskstation\backup\Images\Samsung S5\" "G:\Videos\Samsung S5\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM    --------------------
REM 8. Clone PDF documents.
REM    --------------------
:STEP9
IF EXIST "z:\Z123456789" XXCOPY "%_MYDOCUMENTS%\Administratif\*\*.pdf" "z:\Z123456789\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
IF EXIST "%_CLOUDSTATION%\Documents\Administratif" XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "%_CLOUDSTATION%\Documents\Administratif\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
REM IF [%2] EQU [] (
REM     ECHO:
REM     ECHO:
REM     PAUSE
REM )
SHIFT
GOTO MAIN


REM    -----------------
REM 9. Clone album arts.
REM    -----------------
:STEP10
IF EXIST "z:\Z123456790" XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" "z:\Z123456790\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------
REM 10. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF EXIST "z:\Z123456791" XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /X:*.log /X:*.zip /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -----------------
REM 11. Clone MP4 videos.
REM     -----------------
:STEP12
IF EXIST "z:\Z123456792" XXCOPY "%_CLOUDSTATION%\Vidéos\*.mp4" "z:\Z123456792\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------
REM 12. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
SET _taskid=123456798
python -m Applications.Tables.Tasks.shared select %_taskid% --days 8 --debug
IF %ERRORLEVEL% EQU 0 (
    "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent
    python -m Applications.Tables.Tasks.shared update %_taskid% --debug
)
SHIFT
GOTO MAIN


REM     ------------------------------------------------
REM 15. Clone "\\Diskstation\Images\Collection" to "H:".
REM     ------------------------------------------------
REM STEP14
REM  -->  1. Clone "\\Diskstation\Images\Collection" to "H:". Don't delete extra files and directories!
REM XXCOPY "\\Diskstation\backup\Images\Collection\" "H:\" /CLONE /Z0 /oA:%_XXCOPYLOG%

REM  -->  2. Reverse both source and destination. Then remove brand new files but preserve:
REM          - "RECYCLER".
REM          - "$RECYCLE.BIN".
REM          - "SYSTEM VOLUME INFORMATION".
REM          - "IPHONE".
REM          - "RECOVER".
REM XXCOPY "H:\" "\\Diskstation\backup\Images\Collection\" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%
REM SHIFT
REM GOTO MAIN


REM     -----------------------------------------------
REM 13. Copy audio FLAC files to "\\Diskstation\music".
REM     -----------------------------------------------
:STEP20
XXCOPY "F:\%~2\?*\2\%~3\*\*.flac" "\\Diskstation\music\%~2\" /KS /BI /FF /I /Y /oA:%_XXCOPYLOG%
XXCOPY /CE "\\Diskstation\music\" "F:\" /X:*recycle\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%
SHIFT
SHIFT
SHIFT
GOTO MAIN


REM     -----------------
REM 14. Backup documents.
REM     -----------------
REM     Incremental backup.
REM     Target Group : "workspace.documents".
REM     Target : "Documents (USB Drive)".
:STEP18
IF EXIST "y:" (
    SET _taskid=123456802
    "%_areca%" backup -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg"
    python -m Applications.Tables.Tasks.shared select !_taskid! --days 20 --debug
    IF !ERRORLEVEL! EQU 0 (
       "%_areca%" merge -c -k -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg" -from 0 -to 0
        python -m Applications.Tables.Tasks.shared update !_taskid! --debug
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
REM 15. Move videos to local CloudStation.
REM     ----------------------------------
:STEP19
SET _taskid=123456801
python -m Applications.Tables.Tasks.shared select %_taskid% --days 5 --debug
IF %ERRORLEVEL% EQU 0 (
    PUSHD "%_PYTHONPROJECT%\Tasks\04"
    python main.py
    IF !ERRORLEVEL! EQU 0 python -m Applications.Tables.Tasks.shared update %_taskid% --debug
    POPD
)
SHIFT
GOTO MAIN


REM     ----------------------------
REM 16. Backup AVCHD videos to "X:".
REM     ----------------------------
:STEP24
SHIFT
GOTO MAIN
XXCOPY "G:\Videos\AVCHD Videos\" "X:\Repository\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     --------------------------
REM 17. Sync xreferences database.
REM     --------------------------
:STEP5
PUSHD "%_PYTHONPROJECT%\Tasks\XReferences"
python main.py
POPD
SHIFT
GOTO MAIN
