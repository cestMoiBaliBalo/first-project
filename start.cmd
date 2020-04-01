@ECHO off


@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Production"


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


@REM ==================
@REM Initializations 1.
@REM ==================
SET _me=%~n0
SET _myparent=%~dp0


@REM ==================
@REM Initializations 2.
@REM ==================
SET _mycp=
SET _cp=65001
SET _areca=C:/Program Files/Areca/areca_cl.exe
SET _dailybkp=%_COMPUTING%\Resources\daily_backup.txt
SET _exclusions=%_COMPUTING%\Resources\exclusions2.txt
SET _videos=%USERPROFILE%\videos
SET _xxcopy=xxcopy.cmd


@REM ===============
@REM Main algorithm.
@REM ===============
COLOR 0E


@REM     ---------------------------------------------------
@REM  1. Allow interface to decode UTF-8 encoded characters.
@REM     ---------------------------------------------------

@REM     Set code page.
SET _chcp=
CALL :GET_CODEPAGE _chcp
IF DEFINED _chcp (
    SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)

@REM     Get code page.
CALL :GET_CODEPAGE _chcp
IF DEFINED _chcp @ECHO Code page is %_chcp%.


@REM     -------------------
@REM  2. Run requested task.
@REM     -------------------
:MAIN
IF "%~1" EQU "" (
    @ECHO:
    @ECHO:
    IF DEFINED _mycp (
        CHCP %_mycp% > NUL
        @ECHO Code page is %_mycp%.
    )
    ENDLOCAL
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
IF "%~1" EQU "22" GOTO STEP22
IF "%~1" EQU "23" GOTO STEP23
IF "%~1" EQU "24" GOTO STEP24
IF "%~1" EQU "25" GOTO STEP25
IF "%~1" EQU "26" GOTO STEP26
SHIFT
GOTO MAIN


@REM     --------------------------
@REM  3. Clear temporary directory.
@REM     --------------------------
@REM     /DB#1 Removes files older than or equal to 1 day.
@REM     /RS   Removes files in the source (the only) directory.
@REM     /S    Processes directories and subdirectories except empty ones.
@REM     /R    Deletes even a read-only file.
@REM     /H    Deletes even a hidden/system file.
@REM     /PD0  Suppresses the prompt which would appear on a directory.
@REM     /Y    Suppresses the prompt prior to each file-delete.
@REM     /ED1  Preserves 1 level of empty directories. All subdirectories under %TEMP% are @REMoved.
@REM           Will remove all empty directories under %TEMP%!
:STEP1
XXCOPY /EC %TEMP%\ /RS /S /DB#1 /R /H /Y /PD0 /ED1 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     ---------------------------------------------------------
@REM  4. Remove plain text files from %USERPROFILE%\AppData\Local.
@REM     ---------------------------------------------------------
@REM     /ED   Preserves the directory even if it becomes empty.
:STEP2
XXCOPY /EC %USERPROFILE%\AppData\Local\*.txt /RS /DB#1 /R /H /Y /PD0 /ED /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     ------------------------------
@REM  5. Backup single important files.
@REM     ------------------------------
@REM     /Y:  suppresses prompt when overwriting existing files.
@REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    SET _first=1
    FOR /F "usebackq tokens=* eol=#" %%F IN ("%_dailybkp%") DO (
        SET _switch=/CE
        IF !_first! EQU 1 SET _switch=/EC
        SET _first=0
        CALL SET _file=%%~F
        @ECHO: !_file!
        @REM XXCOPY !_switch! "!_file!" "y:\" /KS /Y /BI /FF /oA:%_XXCOPYLOG%
    )
)
SHIFT
GOTO MAIN


@REM     -----------------------
@REM  6. Remove Areca log files.
@REM     -----------------------
@REM     /DB#14: removes files older than or equal to 14 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\?*\*.log /RS /DB#14 /R /H /Y /PD0 /ED
SHIFT
GOTO MAIN


@REM     ----------
@REM  7. Available.
@REM     ----------
:STEP5
SHIFT
GOTO MAIN


@REM     ----------------------------
@REM  8. Backup %_COMPUTING% content.
@REM     ----------------------------
@REM     /DB#14: removes files older than or equal to 14 days.
@REM     /IA   : copies files only if destination directory doesn't exist.
:STEP6
IF EXIST y:\Computing XXCOPY y:\Computing\ /S /RS /FC /DB#14 /R /H /Y /PD0
XXCOPY %_COMPUTING%\ y:\Computing\/$ymmdd$\ /S /EX:"%_exclusions%" /IA /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     -------------------------------------------------------------------------
@REM  9. Clone "\\Diskstation\backup\Images\Samsung S5" to "G:\Videos\Samsung S5".
@REM     -------------------------------------------------------------------------
@REM     Extra files are deleted.
:STEP7
XXCOPY "\\Diskstation\backup\Images\Samsung S5\" "G:\Videos\Samsung S5\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     --------------------
@REM 10. Clone PDF documents.
@REM     --------------------
:STEP9
IF EXIST "z:" XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "z:\Z123456789\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "%_CLOUDSTATION%\Documents\Administratif\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     -----------------
@REM 11. Clone album arts.
@REM     -----------------
:STEP10
IF EXIST "z:" XXCOPY "%_MYDOCUMENTS%\Album Art\*\*?\*.jpg" "z:\Z123456790\" /IP /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     ---------------------------
@REM 12. Clone MP3Tag configuration.
@REM     ---------------------------
:STEP11
IF EXIST "z:" XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /IP /X:*.log /X:*.zip /CLONE /PZ0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


@REM     -------------------------------
@REM 13. Delete GNUCash sandbox content.
@REM     -------------------------------
:STEP13
SETLOCAL
SET _errorlevel=
SET _taskid=123456798
CALL :CHECK_TASK %_taskid% "8" _errorlevel
IF [%_errorlevel%] EQU [1] (
    @ECHO ===============================
    @ECHO Delete GNUCash sandbox content.
    @ECHO ===============================
    "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && @ECHO GNUCash sandbox content successfully removed.
    CALL :UPDATE_TASK %_taskid% _errorlevel
)
SET _errorlevel=
SET _taskid=
ENDLOCAL
SHIFT
GOTO MAIN


@REM     -----------------
@REM 14. Backup documents.
@REM     -----------------
:STEP18
SETLOCAL
SET _directory=%TEMP%\tmp-Xavier
IF EXIST "y:" (
    SET _errorlevel=
    SET _taskid=123456803
    SET _workspace=%_BACKUP%/workspace.documents/34258241.bcfg
    CALL :CHECK_TASK !_taskid! "4" _errorlevel
    IF [!_errorlevel!] EQU [1] (
        @ECHO:
        @ECHO:
        @ECHO =======================================
        @ECHO Backup personal documents to USB drive.
        @ECHO =======================================
        "%_areca%" backup -c -wdir "!_directory!" -config "!_workspace!" && CALL :UPDATE_TASK !_taskid! _errorlevel
        SET _errorlevel=
        SET _taskid=123456802
        CALL :CHECK_TASK !_taskid! "20" _errorlevel
        IF [!_errorlevel!] EQU [1] "%_areca%" merge -c -k -wdir "!_directory!" -config "!_workspace!" -from 0 -to 0 && CALL :UPDATE_TASK !_taskid! _errorlevel
    )
    SET _errorlevel=
    SET _workspace=
    SET _taskid=
)
IF EXIST "z:" (
    SET _errorlevel=
    SET _taskid=123456804
    SET _workspace=%_BACKUP%/workspace.documents/1282856126.bcfg
    CALL :CHECK_TASK !_taskid! "4" _errorlevel
    IF [!_errorlevel!] EQU [1] (
        @ECHO:
        @ECHO:
        @ECHO ===============================================
        @ECHO Backup personal documents to external WD drive.
        @ECHO ===============================================
        "%_areca%" backup -f -c -wdir "!_directory!" -config "!_workspace!" && CALL :UPDATE_TASK !_taskid! _errorlevel
    )
    SET _errorlevel=
    SET _workspace=
    SET _taskid=
)
SET _directory=
ENDLOCAL
SHIFT
GOTO MAIN


@REM     -----------------------------
@REM 15. Ripped discs Excel dashboard.
@REM     -----------------------------
:STEP22
python "%_PYTHONPROJECT%\AudioCD\Grabber\RippedDiscs.py"
SHIFT
GOTO MAIN


@REM     ----------
@REM 16. Available.
@REM     ----------
:STEP23
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


@REM =================
@REM Shared functions.
@REM =================
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
