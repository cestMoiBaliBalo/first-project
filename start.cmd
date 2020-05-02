@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


@REM ==================
@REM Initializations 1.
@REM ==================
SET _me=%~n0
SET _myparent=%~dp0


@REM ==================
@REM Initializations 2.
@REM ==================
SET _chcp=
SET _mycp=
SET _flag=0
SET _cp=1252
SET _areca=C:/Program Files/Areca/areca_cl.exe
SET _dailybkp=%_COMPUTING%\Resources\daily_backup.txt
SET _exclusions2=%_COMPUTING%\Resources\exclusions2.txt
SET _exclusions3=%_COMPUTING%\Resources\exclusions3.txt
SET _prefixes=ABCDEFGHIJKLMNOPQRSTUVWXYZ
SET _videos=%USERPROFILE%\videos
SET _xxcopy=xxcopy.cmd


@REM ===============
@REM Main algorithm.
@REM ===============


@REM     -----------------------------------------------------
@REM  1. Allow interface to decode Latin-1 encoded characters.
@REM     -----------------------------------------------------

@REM     Set code page.
SET _chcp=
CALL :GET_CODEPAGE _chcp
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

@REM     Get code page.
CALL :GET_CODEPAGE _chcp
IF DEFINED _chcp ECHO Code page is %_chcp%.
ECHO Les caractères accentués sont restitués proprement ^^!
FOR /F "usebackq tokens=*" %%A IN ("%_RESOURCES%\accentuated.txt") DO ECHO %%A


@REM     -------------------
@REM  2. Run requested task.
@REM     -------------------
:MAIN
IF "%~1" EQU "" GOTO THE_END
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
IF "%~1" EQU "22" GOTO STEP22
IF "%~1" EQU "23" GOTO STEP23
IF "%~1" EQU "24" GOTO STEP24
IF "%~1" EQU "25" GOTO STEP25
IF "%~1" EQU "26" GOTO STEP26
SHIFT
GOTO MAIN


@REM      -------------
@REM  3a. Clear %TEMP%.
@REM      -------------
@REM     /DB#1 Removes files older than or equal to 1 day.
@REM     /RS   Removes files in the source (the only) directory.
@REM     /S    Processes directories and subdirectories except empty ones.
@REM     /R    Deletes even a read-only file.
@REM     /H    Deletes even a hidden/system file.
@REM     /PD0  Suppresses the prompt which would appear on a directory.
@REM     /Y    Suppresses the prompt prior to each file-delete.
@REM     /ED1  Preserves %TEMP% but all empty directories under %TEMP% are removed.
@REM     /ED0 would have removed %TEMP%.
@REM     /ED  would have preserved both %TEMP% and empty directories under %TEMP%.
:STEP1
ECHO:
ECHO:
XXCOPY /EC %TEMP%\ /RS /S /DB#1 /R /H /Y /PD0 /ED1 /Xareca_config_backup\ /Xtmp6k11k3_f\ /oA:%_XXCOPYLOG%


@REM      ----------------------------------------
@REM  3b. Then set up a new temporary environment.
@REM      ----------------------------------------
SETLOCAL
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_PYTHONPROJECT%
python temporaryenv.py --files --glob > NUL
POPD
ENDLOCAL
SHIFT
GOTO MAIN


@REM     ---------------------------------------------------------
@REM  4. Remove plain text files from %USERPROFILE%\AppData\Local.
@REM     ---------------------------------------------------------
@REM     /ED   Preserves the directory even if it becomes empty.
:STEP2
ECHO:
ECHO:
XXCOPY /EC %USERPROFILE%\AppData\Local\*.txt /DB#1 /R /H /RSY /PD0 /Y /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     ----------
@REM  5. Available.
@REM     ----------
:STEP3
SHIFT
GOTO MAIN


@REM     -----------------------
@REM  6. Remove Areca log files.
@REM     -----------------------
@REM     /DB#14: removes files older than or equal to 14 days.
:STEP4
IF EXIST %_BACKUP% (
    ECHO:
    ECHO:
    XXCOPY /EC %_BACKUP%\*\?*\*.log /DB#14 /R /H /RSY /PD0 /Y /ED /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


@REM     ----------------------------------------------
@REM  7. Copy single important files to %_MYDOCUMENTS%.
@REM     ----------------------------------------------
@REM     /Y:  suppresses prompt when overwriting existing files.
@REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP5
SET _first=1
FOR /F "usebackq tokens=* eol=#" %%F IN ("%_dailybkp%") DO (
    SET _switch=/CE
    IF !_first! EQU 1 SET _switch=/EC
    SET _first=0
    CALL SET _file=%%~F
    ECHO:
    ECHO:
    XXCOPY !_switch! "!_file!" %_MYDOCUMENTS%\ /KS /Y /BI /FF /oA:%_XXCOPYLOG%
    )
SET _first=
SET _switch=
SHIFT
GOTO MAIN


@REM     ----------------------------
@REM  8. Backup %_COMPUTING% content.
@REM     ----------------------------
@REM     /DB#21: removes files older than or equal to 21 days.
@REM     /IA   : copies files only if destination directory doesn't exist.
:STEP6
IF EXIST y:\Computing (

:STEP6A
    ECHO:
    ECHO:
    XXCOPY /EC y:\Computing\ /S /RS /FC /DB#21 /R /H /Y /PD0

:STEP6B
    ECHO:
    ECHO:
    SET _prefix=
    SET _count=-1

:STEP6C
    XXCOPY /EC %_COMPUTING%\ y:\Computing\/$ymmdd$!_prefix!\ /S /EX:"%_exclusions2%" /IA /KS /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 47 (
        SHIFT
        GOTO MAIN
    )
    IF ERRORLEVEL 46 (
        CALL :GET_PREFIX _count _prefix
        IF DEFINED _prefix GOTO STEP6C
    )
)
SHIFT
GOTO MAIN


@REM     -------------------------------------------------------------------------
@REM  9. Clone "\\Diskstation\backup\Images\Samsung S5" to "G:\Videos\Samsung S5".
@REM     -------------------------------------------------------------------------
@REM     Extra files are deleted.
:STEP7
@REM SET _switch=
@REM CALL :GET_SWITCH _flag _switch
@REM XXCOPY /EC "\\Diskstation\backup\Images\Samsung S5\" "G:\Videos\Samsung S5\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     --------------------
@REM 10. Clone PDF documents.
@REM     --------------------
@REM     Extra files are deleted.
:STEP9
IF EXIST z: (
    ECHO:
    ECHO:
    XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "z:\Z123456789\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
)
ECHO:
ECHO:
XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "%_CLOUDSTATION%\Documents\Administratif\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     -----------------
@REM 11. Clone album arts.
@REM     -----------------
@REM     Extra files are deleted.
:STEP10
IF EXIST z: (
    ECHO:
    ECHO:
    XXCOPY /EC "%_MYDOCUMENTS%\Album Art\*\*?\*.jpg" "z:\Z123456790\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


@REM     ---------------------------
@REM 12. Clone MP3Tag configuration.
@REM     ---------------------------
@REM     Extra files are deleted.
:STEP11
IF EXIST z: (
    ECHO:
    ECHO:
    XXCOPY /EC "%APPDATA%\MP3Tag\" "z:\Z123456791\" /IP /X:*.log /X:*.zip /CLONE /PZ0 /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


@REM     -------------------------------
@REM 13. Delete GNUCash sandbox content.
@REM     -------------------------------
:STEP13
SETLOCAL
SET _taskid=123456798
CALL :CHECK_TASK %_taskid% "8"
IF ERRORLEVEL 1 (
    @ECHO:
    @ECHO:
    @ECHO ===============================
    @ECHO Delete GNUCash sandbox content.
    @ECHO ===============================
    "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && @ECHO GNUCash sandbox content successfully removed.
    CALL :UPDATE_TASK %_taskid%
)
SET _taskid=
ENDLOCAL
SHIFT
GOTO MAIN


@REM     ----------
@REM 14. Available.
@REM     ----------
:STEP18
SHIFT
GOTO MAIN


@REM     -----------------------------
@REM 15. Ripped discs Excel dashboard.
@REM     -----------------------------
:STEP22
python "%_PYTHONPROJECT%\AudioCD\Grabber\RippedDiscs.py"
SHIFT
GOTO MAIN


@REM     ------------------------------
@REM 16. Backup %_MYDOCUMENTS% content.
@REM     ------------------------------
@REM     /DB#21: removes files older than or equal to 21 days.
@REM     /IA   : copies files only if destination directory doesn't exist.
:STEP23
IF EXIST y:\Documents (

:STEP23A
    ECHO:
    ECHO:
    XXCOPY /EC y:\Documents\ /S /RS /FC /DB#21 /R /H /Y /PD0

:STEP23B
    ECHO:
    ECHO:
    SET _prefix=
    SET _count=-1

:STEP23C
    XXCOPY /EC %_MYDOCUMENTS%\ y:\Documents\/$ymmdd$!_prefix!\ /IA /KS /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 47 (
        SHIFT
        GOTO MAIN
    )
    IF ERRORLEVEL 46 (
        CALL :GET_PREFIX _count _prefix
        IF DEFINED _prefix GOTO STEP23C
    )
)
SHIFT
GOTO MAIN


@REM     -------------------------------
@REM 17. Backup AVCHD videos to X drive.
@REM     -------------------------------
:STEP24
XXCOPY "G:\Videos\AVCHD Videos\" "X:\Repository\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     ----------
@REM 18. Available.
@REM     ----------
:STEP25
SHIFT
GOTO MAIN


@REM     ----------
@REM 19. Available.
@REM     ----------
:STEP26
SHIFT
GOTO MAIN


:THE_END
ECHO:
ECHO:
IF DEFINED _mycp (
    CHCP %_mycp% > NUL
    ECHO Code page is now %_mycp%.
    SET _mycp=
)
ENDLOCAL
PAUSE
EXIT /B %ERRORLEVEL%


@REM =================
@REM Shared functions.
@REM =================
:CHECK_TASK
python -m Applications.Tables.Tasks.shared "%~1" check --delta "%~2"
EXIT /B %ERRORLEVEL%


:UPDATE_TASK
python -m Applications.Tables.Tasks.shared "%~1" update
EXIT /B %ERRORLEVEL%


:DELAY_TASK
python -m Applications.Tables.Tasks.shared "%~1" update %~2 "%~3"
SET %~4=%ERRORLEVEL%
EXIT /B 0


:GET_CODEPAGE
SETLOCAL
SET _chcp=
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO SET _chcp=%%J
(
    SET _chcp=
    ENDLOCAL
    SET %1=%_chcp%
)
EXIT /B 0


:GET_SWITCH
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _flag=!%~1!
SET _switch=/EC
IF %_flag% EQU 1 SET _switch=/CE
IF %_flag% EQU 0 SET _flag=1
(
    ENDLOCAL
    SET %1=%_flag%
    SET %2=%_switch%
)
EXIT /B 0


:GET_PREFIX
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _count=!%~1!
:LOOP
(
    SET _prefix=
    SET /A "_count+=1"
    IF !_count! LEQ 25 CALL SET _prefix=%%_prefixes:~!_count!,1%%
)
(
    SET _count=
    SET _prefix=
    ENDLOCAL
    SET %1=%_count%
    SET %2=%_prefix%
)
EXIT /B 0
