@ECHO off


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
SET _dailybkp=%_COMPUTING%\Resources\daily_backup.txt
SET _exclusions=%_COMPUTING%\\Resources\exclusions2.txt
SET _videos=%USERPROFILE%\videos
SET _xxcopy=xxcopy.cmd


REM ===============
REM Main algorithm.
REM ===============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp%


REM     ------
REM  2. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" (
    ECHO:
    ECHO:
    PAUSE
    EXIT /B %ERRORLEVEL%
)
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
IF "%~1" EQU "6" GOTO STEP6
IF "%~1" EQU "7" GOTO STEP7
IF "%~1" EQU "9" GOTO STEP9
IF "%~1" EQU "10" GOTO STEP10
IF "%~1" EQU "11" GOTO STEP11
IF "%~1" EQU "13" GOTO STEP13
IF "%~1" EQU "18" GOTO STEP18
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
REM     /ED1  Preserves 1 level of empty directories. All subdirectories under %TEMP% are REMoved.
REM           Will remove all empty directories under %TEMP%!
:STEP1
XXCOPY /EC %TEMP%\ /RS /S /DB#1 /R /H /Y /PD0 /ED1 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------------------------------------
REM  4. Remove plain text files from %USERPROFILE%\AppData\Local.
REM     ---------------------------------------------------------
REM     /ED   Preserves the directory even if it becomes empty.
:STEP2
XXCOPY /EC %USERPROFILE%\AppData\Local\*.txt /RS /DB#1 /R /H /Y /PD0 /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ------------------------------
REM  5. Backup single important files.
REM     ------------------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    SET _first=1
    FOR /F "usebackq tokens=*" %%F IN ("%_dailybkp%") DO (
        SET _switch=/CE
        IF !_first! EQU 1 SET _switch=/EC
        SET _first=0
        CALL SET _file=%%~F
        XXCOPY !_switch! "!_file!" "y:\" /KS /Y /BI /FF /oA:%_XXCOPYLOG%
    )
)
SHIFT
GOTO MAIN


REM     -----------------------
REM  6. Remove Areca log files.
REM     -----------------------
REM     /DB#14: removes files older than or equal to 14 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\?*\*.log /RS /DB#14 /R /H /Y /PD0 /ED
SHIFT
GOTO MAIN


REM     ----------------------------
REM  7. Backup %_COMPUTING% content.
REM     ----------------------------
REM     /DB#14: removes files older than or equal to 14 days.
REM     /IA   : copies files only if destination directory doesn't exist.
:STEP6
IF EXIST y:\Computing XXCOPY y:\Computing\ /S /RS /FC /DB#14 /R /H /Y /PD0
XXCOPY %_COMPUTING%\ y:\Computing\/$ymmdd$\ /S /EX:"%_exclusions%" /IA /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------------------------------------------------
REM  8. Clone "\\Diskstation\backup\Images\Samsung S5" to "G:\Videos\Samsung S5".
REM     -------------------------------------------------------------------------
REM     Extra files are deleted.
:STEP7
XXCOPY "\\Diskstation\backup\Images\Samsung S5\" "G:\Videos\Samsung S5\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     --------------------
REM  9. Clone PDF documents.
REM     --------------------
:STEP9
XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "z:\Z123456789\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "%_CLOUDSTATION%\Documents\Administratif\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -----------------
REM 10. Clone album arts.
REM     -----------------
:STEP10
XXCOPY "%_MYDOCUMENTS%\Album Art\*\*?\*.jpg" "z:\Z123456790\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------
REM 11. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /IP /X:*.log /X:*.zip /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------
REM 12. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
SET _errorlevel=
SET _taskid=123456798
CALL :CHECK_TASK %_taskid% "8" _errorlevel
IF [%_errorlevel%] EQU [1] (
    ECHO -------------------------------
    ECHO Delete GNUCash sandbox content.
    ECHO -------------------------------
    "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && ECHO GNUCash sandbox content successfully removed.
    CALL :UPDATE_TASK %_taskid% _errorlevel
)
SHIFT
GOTO MAIN


REM     -----------------
REM 13. Backup documents.
REM     -----------------
:STEP18
SET _directory=%TEMP%\tmp-Xavier
IF EXIST "y:" (
    SET _errorlevel=
    SET _taskid=123456803
    SET _workspace=%_BACKUP%/workspace.documents/34258241.bcfg
    CALL :CHECK_TASK !_taskid! "4" _errorlevel
    IF [!_errorlevel!] EQU [1] (
        ECHO:
        ECHO:
        ECHO ---------------------------------------
        ECHO Backup personal documents to USB drive.
        ECHO ---------------------------------------
        "%_areca%" backup -c -wdir "!_directory!" -config "!_workspace!" && CALL :UPDATE_TASK !_taskid! _errorlevel
        SET _errorlevel=
        SET _taskid=123456802
        CALL :CHECK_TASK !_taskid! "20" _errorlevel
        IF [!_errorlevel!] EQU [1] "%_areca%" merge -c -k -wdir "!_directory!" -config "!_workspace!" -from 0 -to 0 && CALL :UPDATE_TASK !_taskid! _errorlevel
    )
    SET _workspace=
    SET _taskid=
)
IF EXIST "z:" (
    SET _errorlevel=
    SET _taskid=123456804
    SET _workspace=%_BACKUP%/workspace.documents/1282856126.bcfg
    CALL :CHECK_TASK !_taskid! "4" _errorlevel
    IF [!_errorlevel!] EQU [1] (
        ECHO:
        ECHO:
        ECHO -----------------------------------------------
        ECHO Backup personal documents to external WD drive.
        ECHO -----------------------------------------------
        "%_areca%" backup -f -c -wdir "!_directory!" -config "!_workspace!" && CALL :UPDATE_TASK !_taskid! _errorlevel
    )
    SET _workspace=
    SET _taskid=
)
SET _directory=
SHIFT
GOTO MAIN


REM     -------------------------
REM 15. Backup AVCHD videos to X.
REM     -------------------------
:STEP24
XXCOPY "G:\Videos\AVCHD Videos\" "X:\Repository\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     --------------------------
REM 16. Sync xreferences database.
REM     --------------------------
:STEP5
ECHO:
ECHO:
ECHO ----------------------------
ECHO Sync audio cross-references.
ECHO ----------------------------
SET _elapsed=
SET _inserted=
SET _removed=
ECHO It can take a while.
PUSHD "%_PYTHONPROJECT%\Tasks\XReferences"
python main.py
PUSHD "%TEMP%"
IF EXIST "tempfile.txt" FOR /F "usebackq delims=| tokens=1-3" %%I IN ("tempfile.txt") DO (
    SET _elapsed=%%I
    SET _inserted=%%J
    SET _removed=%%K
)
POPD
POPD
ECHO Done.
IF DEFINED _inserted ECHO %_inserted% albums inserted.
IF DEFINED _removed ECHO %_removed% albums removed.
SHIFT
GOTO MAIN


REM     ----------------------------------------
REM 17. Backup personal files to SD memory card.
REM     ----------------------------------------
REM     Every 28 days.
:STEP25
SET _errorlevel=
SET _taskid=123456800
CALL :CHECK_TASK %_taskid% "28" _errorlevel
IF [!_errorlevel!] EQU [1] (
    CLS
    CHOICE /N /C YN /T 30 /D N /M "Would you like to refresh the backup? Press [Y] for Yes or [N] for No."
    IF ERRORLEVEL 2 GOTO DELAY
    CLS
    ECHO Insert SD Memory Card then press any key to run the backup... && PAUSE > NUL
    CLS
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD %_PYTHON_SECONDPROJECT%
    python backup.py
    IF ERRORLEVEL 1 (
        POPD
        GOTO FIN
    )
    PUSHD "%TEMP%"
    IF EXIST "%_xxcopy%" CALL "%_xxcopy%"
    GOTO UPDATE
)
GOTO FIN

:DELAY
CALL :DELAY_TASK %_taskid% "sub" "23" _errorlevel
GOTO FIN

:UPDATE
POPD
POPD
CALL :UPDATE_TASK %_taskid% _errorlevel
ECHO:
ECHO:
PAUSE
GOTO FIN

:FIN
SHIFT
GOTO MAIN


REM -----------------
REM Shared functions.
REM -----------------
:CHECK_TASK
python -m Applications.Tables.Tasks.shared "%~1" check --delta "%~2"
SET %~3=%ERRORLEVEL%
EXIT /B 0


:UPDATE_TASK
python -m Applications.Tables.Tasks.shared "%~1" update
SET %~2=%ERRORLEVEL%
EXIT /B 0


:DELAY_TASK
python -m Applications.Tables.Tasks.shared "%~1" update %~2 "%~3"
SET %~4=%ERRORLEVEL%
EXIT /B 0
