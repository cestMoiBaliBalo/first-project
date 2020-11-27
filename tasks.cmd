@ECHO off


REM __author__ = Xavier ROSSET
REM __maintainer__ = Xavier ROSSET
REM __email__ = xavier.python.computing@protonmail.com
REM __status__ = Production


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _xxcopy=xxcopy.cmd
SET _cp=65001


REM ============
REM Main script.
REM ============
PUSHD %_myparent%MyPythonProject


REM ----------------------
REM Set console code page.
REM ----------------------
PUSHD ..\Resources
SET _step=1
CALL shared.cmd
IF DEFINED _chcp (
    IF NOT DEFINED _mycp SET _mycp=%_chcp%
    IF [%_chcp%] NEQ [%_cp%] CHCP %_cp% > NUL
)
POPD


REM -------------
REM Display menu.
REM -------------
:MENU
python Tasks\Manager\main.py


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM -----------------------------------------
REM Sync PDF documents to local CloudStation.
REM -----------------------------------------
IF ERRORLEVEL 36 (
    CLS
    PUSHD ..
    C:\Windows\System32\cmd.exe /C start.cmd 9
    POPD
    PAUSE
    GOTO MENU
)


REM ---------------------------------------------
REM Sync local audio database with digital discs.
REM ---------------------------------------------
REM HDtracks.com, nugs.net, etc.
IF ERRORLEVEL 35 (
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    PUSHD ..
    CALL insertDigitalDiscs_main.cmd
    POPD
    ENDLOCAL
    GOTO MENU
)


REM --------------------------
REM Sync targets repositories.
REM --------------------------
IF ERRORLEVEL 34 (
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    PUSHD Backup
    python targets.py %_BACKUP%\workspace.music
    POPD
    ENDLOCAL
    GOTO MENU
)


IF ERRORLEVEL 33 (
:LOOP33
    CLS
    TYPE %_myparent%Resources\digital_bootlegs_audiotags_bs.txt
    ECHO:
    ECHO:
    ECHO:
    SET /P _answer=Enter requested action: 
    IF [!_answer!] EQU [99] GOTO MENU
    IF [!_answer!] EQU [2] (
        PUSHD %TEMP%
        IF EXIST %_xxcopy% (
            CLS
            CALL %_xxcopy%
            ECHO:
            ECHO:
            PAUSE
        )
        POPD
        GOTO LOOP33
    )
    IF [!_answer!] EQU [1] (
        IF EXIST %TEMP%\%_xxcopy% (
            CLS
            TYPE %TEMP%\%_xxcopy%
            ECHO:
            ECHO:
            PAUSE
        )
        GOTO LOOP33
    )
)


IF ERRORLEVEL 32 (
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET _commandsfile=rippedtracks.cmd
    SET _tracksfile=rippedtracks.txt
    IF EXIST "\\diskstation\music" (
        PUSHD ..\Resources
        IF EXIST !_commandsfile! (
            CLS
            CALL !_commandsfile! 0 && DEL !_commandsfile! && DEL !_tracksfile! 2> NUL
            ECHO:
            ECHO:
            PAUSE
        )
        POPD
    )
    ENDLOCAL
    GOTO MENU
)


REM ---------------------------------------------
REM Dump ripped discs collection into a CSV file.
REM ---------------------------------------------
REM Data are taken from the local audio database.
IF ERRORLEVEL 31 (
    PUSHD Tasks
    python getRippedDiscs.py
    POPD
    GOTO MENU
)


REM -------------------------
REM Update discs played date.
REM -------------------------
REM Manual update.
IF ERRORLEVEL 30 (
    PUSHD Interfaces\Sources\06
    python main.py
    POPD
    GOTO MENU
)


REM -------------------------
REM Update discs played date.
REM -------------------------
REM Batch update from iTunes music library.
IF ERRORLEVEL 29 (
    CLS
    SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    SET _results=playeddiscs.txt 
    python Tasks\updatePlayedDiscs.py
    SET _errorlevel=!ERRORLEVEL!
    IF !_errorlevel! GTR 0 (
        PUSHD %TEMP%
        IF EXIST !_results! (
            ECHO:
            TYPE !_results!
            ECHO:
            ECHO:
            ECHO:
            PAUSE
        )
        POPD
    )
    ENDLOCAL
    GOTO MENU
)


REM ------------------------
REM Additional backup tasks.
REM ------------------------
IF ERRORLEVEL 28 (
    PUSHD ..\Resources

:LOOP28
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET PATH=%_myparent%MyPythonProject\VirtualEnv\venv38\Scripts;!PATH!
    PUSHD ..\MyPythonProject\Tasks\Manager
    python music.py
    IF ERRORLEVEL 100 (
        POPD
        ENDLOCAL
        CALL backup.cmd "music" !ERRORLEVEL!
        ECHO:
        ECHO:
        PAUSE
        GOTO LOOP28
    )
    IF ERRORLEVEL 99 (
        POPD
        ENDLOCAL
        POPD
        GOTO MENU
    )

)


REM -------------------------------------------------------
REM Copy HDtracks.com lossless audio files to backup drive.
REM -------------------------------------------------------
IF ERRORLEVEL 27 (
    CLS
    IF EXIST z: (
        XXCOPY /EC %_MYMUSIC%\HDtracks\ z:\HDtracks\ /S /KS /RCY /PD0 /ED1 /oA%_XXCOPYLOG%
        ECHO:
        ECHO:
        PAUSE
    )
    GOTO MENU
)


REM ----------------------------------------------
REM Copy single lossy audio files to backup drive.
REM ----------------------------------------------
REM Both M4A and MP3 without lossless version (iTunes, amazon, etc).
IF ERRORLEVEL 26 (
    CLS
    PUSHD ..
    CALL backupLossyFiles.cmd T
    POPD
    GOTO MENU
)


REM -----------------------------------------------
REM Backup AVCHD videos collection to backup drive.
REM -----------------------------------------------
REM It is a one way syncing! Extra files are preserved.
IF ERRORLEVEL 25 (

    CLS
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _collection=G:\Videos\AVCHD Videos
    PUSHD ..\Resources
    SET _drive=
    SET _step=6
    SET _type=3
    SET _name=AVCHD
    CALL shared.cmd
    IF NOT DEFINED _drive (
        ECHO No drive named AVCHD. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END25
    )

    REM 1. Check if new videos have been inserted since the previous sync.
    CLS
    ECHO Check if new videos have been inserted since the previous sync...
    XXCOPY "!_collection!\" "!_drive!\" /L /ZS /Q3 /CLONE /Z0 /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        ECHO Syncing is not required. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END25
    )

    REM 2. Clone collection to backup drive. Don't delete extra files and directories!
    CLS
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy videos to local drive !_drive:~0,-1!."
    IF NOT DEFINED _answer GOTO END25
    IF [!_answer!] EQU [N] GOTO END25
    CLS
    XXCOPY /EC "!_collection!\" "!_drive!\" /CLONE /Z0 /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:END25
    POPD
    ENDLOCAL
    GOTO MENU

)


REM ------------------------------------------------------
REM Clone MyCloud Samsung S5 images from local collection.
REM ------------------------------------------------------
REM It is a two ways syncing! Extra files are deleted.
IF ERRORLEVEL 24 (

    CLS
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _local_collection=G:\Videos\Samsung S5
    SET _cloud_collection=\\DISKSTATION\backup\Images\Samsung S5

    REM 1. Check if new images have been inserted since the previous sync.
    CLS
    ECHO Check if new images have been inserted/removed since the previous sync...
    XXCOPY "!_local_collection!\" "!_cloud_collection!\" /L /ZS /Q3 /CLONE /PZ0 /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        ECHO Syncing is not required. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END24
    )

    REM 2. Clone MyCloud. Delete extra files!
    CLS
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will clone images to distant drive with extra files removal."
    IF NOT DEFINED _answer GOTO END24
    IF [!_answer!] EQU [N] GOTO END24
    CLS
    XXCOPY /EC "!_local_collection!\" "!_cloud_collection!\" /ZS /CLONE /PZ0 /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:END24
    ENDLOCAL
    GOTO MENU

)


REM -------------------------------------------
REM Clone MyCloud images from local collection.
REM -------------------------------------------
REM Local collection MUST be the master collection!
REM It is a two ways syncing! Extra files are deleted.
IF ERRORLEVEL 23 (

    CLS
    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _cloud_collection=\\DISKSTATION\backup\Images\Collection
    PUSHD ..\Resources
    SET _drive=
    SET _step=6
    SET _type=3
    SET _name=PICTURES
    CALL shared.cmd
    IF NOT DEFINED _drive (
        ECHO No drive named PICTURES. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END23
    )
    DEL %TEMP%\NewFiles.txt 2> NUL
    DEL %TEMP%\SyncedFiles.txt 2> NUL

    REM 1. Check at first if new images have been inserted into MyCloud since the previous task.
    ECHO Check if brand new images have been inserted into MyCloud since the previous task...
    ECHO:
    ECHO:
    XXCOPY "!_cloud_collection!\*\?*\*.jpg" "!_drive!\" /L /BB /ZS /Q3 /Fo%TEMP%\NewFiles.txt /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        CLS
        ECHO No brand new images found into MyCloud.
        ECHO:
        ECHO:
        PAUSE
    )
    IF NOT ERRORLEVEL 1 IF ERRORLEVEL 0 (
        CLS
        ECHO Some brand new images have been found into MyCloud. Please check %TEMP%\NewFiles.txt.
        ECHO:
        ECHO:
        PAUSE
        CLS
        CHOICE /C YNA /N /CS /T 20 /D A /M "Would you like to copy new distant images to the local collection? Press [Y] for Yes, [N] for No or [A] for Aborting copy."
        IF ERRORLEVEL 3 GOTO END23
        IF NOT ERRORLEVEL 2 IF ERRORLEVEL 1 (
            CLS
            XXCOPY "!_cloud_collection!\*\?*\*.jpg" "!_drive!\" /BB /ZS /oA:%_XXCOPYLOG%
            ECHO:
            ECHO:
            PAUSE
        )
    )

    REM 2. Check if syncing is required.
    CLS
    ECHO Check now if syncing is required...
    ECHO:
    ECHO:
    XXCOPY "!_drive!\*\?*\*.jpg" "!_cloud_collection!\" /L /ZS /Q3 /CLONE /PZ0 /Fo%TEMP%\SyncedFiles.txt /oA:%_XXCOPYLOG% /X:$RECYCLE.BIN\
    IF ERRORLEVEL 1 (
        CLS
        ECHO Syncing is not required. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END23
    )
    IF NOT ERRORLEVEL 1 IF ERRORLEVEL 0 (
        CLS
        ECHO Syncing is required^^!
        ECHO:
        ECHO:
        PAUSE
    )

    REM 3. Clone MyCloud from local collection.
    CLS
    ECHO Clone now MyCloud from local collection...
    ECHO:
    ECHO:
    PAUSE
    CLS
    CALL :QUESTION "YN" "20" "N" "Please confirm your choice as XXCOPY application will copy images from local drive !_drive:~0,-1! to MyCloud with extra files removal."
    IF NOT DEFINED _answer GOTO END23
    IF [!_answer!] EQU [N] GOTO END23
    CLS
    XXCOPY /EC "!_drive!\*\?*\*.jpg" "!_cloud_collection!\" /ZS /CLONE /PZ0 /Fo%TEMP%\SyncedFiles.txt /oA:%_XXCOPYLOG% /X:$RECYCLE.BIN\
    ECHO:
    ECHO:
    PAUSE

:END23
    POPD
    ENDLOCAL
    GOTO MENU

)


REM ---------------------------
REM Run continuous integration.
REM ---------------------------
IF ERRORLEVEL 22 (
    CLS
    ECHO:
    C:\Windows\System32\cmd.exe /C G:\Computing\MyPythonProject\AudioCD\Grabber\grab_main.cmd 2
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM -----------------------------------------------
REM Dump bootleg albums collection into a CSV file.
REM -----------------------------------------------
REM Data are taken from the local audio database.
IF ERRORLEVEL 21 (
    PUSHD Tasks
    python getBootlegAlbums.py bootleg
    POPD
    GOTO MENU
)


REM ----------
REM Available.
REM ----------
IF ERRORLEVEL 20 GOTO MENU


REM ----------
REM Available.
REM ----------
IF ERRORLEVEL 19 GOTO MENU


REM -----------------------------------------------
REM Clone AVCHD videos collection to distant drive.
REM -----------------------------------------------
REM It is a two ways syncing! Extra files are deleted.
IF ERRORLEVEL 18 (

    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    SET _cloud_avchd=\\DISKSTATION\backup\AVCHD Vidéos
    SET _local_avchd=G:\Videos\AVCHD Videos

    REM 1. Check if new videos have been inserted since the previous sync.
    CLS
    ECHO Check if new videos have been inserted since the previous sync...
    XXCOPY "!_local_avchd!\" "!_cloud_avchd!\" /L /ZS /Q3 /CLONE /PZ0 /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        ECHO Syncing is not required. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END18
    )

    REM 2. Clone collection to distant drive. Delete extra files and directories!
    CLS
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy videos to distant drive."
    IF NOT DEFINED _answer GOTO END18
    IF [!_answer!] EQU [N] GOTO END18
    CLS
    XXCOPY /EC "!_local_avchd!\" "!_cloud_avchd!\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:END18
    ENDLOCAL
    GOTO MENU

)


REM -------------------------
REM Sync MyCloud audio files.
REM -------------------------
IF ERRORLEVEL 17 (
    CLS
    DEL %TEMP%\%_xxcopy% 2> NUL
    PUSHD Interfaces\Sources\01
    python main.py --repository MyCloud
    IF NOT ERRORLEVEL 1 CALL :CONFIRM
    POPD
    GOTO MENU
)


REM --------------------------------------------------
REM Sync mobile devices from local audio repositories.
REM --------------------------------------------------
IF ERRORLEVEL 16 (
    CLS
    DEL %TEMP%\%_xxcopy% 2> NUL
    PUSHD Interfaces\Sources\02
    python main.py
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        POPD
        GOTO MENU
    )
    PUSHD %TEMP%
    IF EXIST %_xxcopy% CALL %_xxcopy%
    ECHO:
    ECHO:
    PAUSE
    POPD
    POPD
    GOTO MENU
)


REM -----------------------------------------------
REM Clone local Samsung S5 collection from MyCloud.
REM -----------------------------------------------
REM It is a two ways syncing! Extra files are deleted.
IF ERRORLEVEL 15 (

    SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
    PUSHD G:\Videos\Samsung S5

    REM 1. Check if new images have been inserted since the previous sync.
    CLS
    ECHO Check if new images have been inserted/removed since the previous sync...
    XXCOPY "\\DISKSTATION\backup\Images\Samsung S5\" /L /ZS /Q3 /CLONE /PZ0 /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        ECHO Syncing is not required. Task is going to be aborted^^!
        ECHO:
        ECHO:
        PAUSE
        GOTO END15
    )

    REM 2. Clone collection to local drive. Delete extra files!
    CLS
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will clone images to local drive with extra files removal."
    IF NOT DEFINED _answer GOTO END15
    IF [!_answer!] EQU [N] GOTO END15
    CLS
    XXCOPY /EC "\\DISKSTATION\backup\Images\Samsung S5\" /CLONE /PZ0 /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:END15
    POPD
    ENDLOCAL
    GOTO MENU

)


REM ----------------------------------
REM Display bootleg albums collection.
REM ----------------------------------
REM Data are taken from FLAC files Vorbis comments.
IF ERRORLEVEL 14 (
    REM CLS
    REM PUSHD Tasks
    REM python getBootlegAlbums.py "F:\M\Metallica\2" "F:\P\Pearl Jam\2" "F:\S\Springsteen, Bruce\2"
    REM POPD
    REM ECHO:
    REM ECHO:
    REM ECHO:
    REM ECHO:
    REM PAUSE
    GOTO MENU
)


REM ------------------------------
REM Sync local audio repositories.
REM ------------------------------
IF ERRORLEVEL 13 (
    CLS
    DEL %TEMP%\%_xxcopy% 2> NUL
    PUSHD Interfaces\Sources\01
    python main.py
    IF NOT ERRORLEVEL 1 CALL :CONFIRM
    POPD
    GOTO MENU
)


REM ----------
REM Available.
REM ----------
IF ERRORLEVEL 12 GOTO MENU


REM -------------------------------
REM List python installed packages.
REM -------------------------------
IF ERRORLEVEL 11 (

:LOOP11
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET _name=
    SET _venv=
    CALL :GET_VIRTUALENV 0
    IF ERRORLEVEL 100 (
        ENDLOCAL
        GOTO MENU
    )
    CLS
    SET PATH=!_venv!;!PATH!
    pip list
    ECHO:
    ECHO:
    PAUSE
    ENDLOCAL
    GOTO LOOP11

)


REM ------------------------------
REM List Python outdated packages.
REM ------------------------------
IF ERRORLEVEL 10 (

:LOOP10
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET _name=
    SET _venv=
    CALL :GET_VIRTUALENV 0
    IF ERRORLEVEL 100 (
        ENDLOCAL
        GOTO MENU
    )
    CLS
    SET PATH=!_venv!;!PATH!
    pip list -o
    ECHO:
    ECHO:
    PAUSE
    ENDLOCAL
    GOTO LOOP10

)


REM ------------
REM Upgrade pip.
REM ------------
IF ERRORLEVEL 9 (

:LOOP9
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET _name=
    SET _venv=
    CALL :GET_VIRTUALENV 0
    IF ERRORLEVEL 100 (
        ENDLOCAL
        GOTO MENU
    )
    CLS
    SET PATH=!_venv!;!PATH!
    python -m pip install --upgrade pip
    ECHO:
    ECHO:
    PAUSE
    ENDLOCAL
    GOTO LOOP9

)


REM -------------------------------------
REM Toggle to python virtual environment.
REM -------------------------------------
IF ERRORLEVEL 8 (

:STEP8A
    SET _name=
    SET _venv=
    CALL :GET_VIRTUALENV 1
    IF ERRORLEVEL 100 GOTO STEP8B
    CLS
    CALL "%_myparent%environment.cmd" A !_name!
    CMD /K PROMPT [!_name! environment]$G
    CALL "%_myparent%environment.cmd" D
    GOTO STEP8A

:STEP8B
    SET _name=
    SET _venv=
    GOTO MENU

)


REM ---------------------
REM Backup artists [U-Z].
REM ---------------------
IF ERRORLEVEL 6 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 204959095
    POPD
    GOTO MENU
)


REM ---------------------
REM Backup artists [P-T].
REM ---------------------
IF ERRORLEVEL 5 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 1535780732
    POPD
    GOTO MENU
)


REM ---------------------
REM Backup artists [K-O].
REM ---------------------
IF ERRORLEVEL 4 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 1196865155
    POPD
    GOTO MENU
)


REM ---------------------
REM Backup artists [F-J].
REM ---------------------
IF ERRORLEVEL 3 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 1674209532
    POPD
    GOTO MENU
)


REM ---------------------
REM Backup artists [A-E].
REM ---------------------
IF ERRORLEVEL 2 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 854796030
    POPD
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    PUSHD ..\Resources
    CALL backup.cmd "music" 854796030 1674209532 1196865155 1535780732 204959095
    POPD
    GOTO MENU
)


REM ==========
REM Exit menu.
REM ==========
:EXIT
POPD
ENDLOCAL
CLS
EXIT /B 0


REM ================
REM Local functions.
REM ================


:QUESTION
SETLOCAL
SET _answer=Y
ECHO:
ECHO:
CHOICE /C %~1 /T %~2 /N /D %~3 /M "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET _answer=N
(
    ENDLOCAL
    SET _answer=%_answer%
)
EXIT /B 0


:CONFIRM
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
PUSHD %TEMP%
IF EXIST %_xxcopy% (
    CLS
    ECHO The following XXCOPY commands will be run:
    ECHO:
    ECHO:
    FOR /F "usebackq tokens=1,* delims=." %%I IN ("%_xxcopy%") DO IF [%%I] EQU [XXCOPY] CALL ECHO %%I.%%J
    ECHO:
    ECHO:
    CALL :QUESTION "YN" "90" "N" "Would you like to continue? "
    IF DEFINED _answer IF [!_answer!] EQU [Y] (
        CLS
        CALL %_xxcopy%
        ECHO:
        ECHO:
        PAUSE
    )
)
POPD
ENDLOCAL
EXIT /B 0


REM ===============================================
REM GET THE LIST OF AVAILABLE VIRTUAL ENVIRONMENTS.
REM ===============================================
:GET_VIRTUALENV
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
PUSHD VirtualEnv
SET _index=0
SET _exit=0
SET _name=
SET _venv=

:R01_STEP1
CLS

REM -----
IF %~1 EQU 0 (
    ECHO:
    ECHO Available (virtual^) environment(s^):
    ECHO:
)
IF %~1 EQU 1 (
    ECHO:
    ECHO Available virtual environment(s^):
    ECHO:
)
REM -----
IF %~1 EQU 0 (
    SET _index=1
    ECHO:  !_index!. Default environment.
    SET _dir01=%LOCALAPPDATA%\Programs\Python\Python37-32\Scripts
)

REM -----
FOR /F "usebackq tokens=*" %%A IN (`DIR /B /AD /ON`) DO (
    SET /A "_index+=1"
    SET _ok=0
    IF !_ok! EQU 0 IF !_index! LEQ 9 (
        ECHO:  !_index!. %%~A.
        SET _dir0!_index!=%%~A
        SET _ok=1
    )
    IF !_ok! EQU 0 IF !_index! LEQ 99 (
        ECHO: !_index!. %%~A.
        SET _dir!_index!=%%~A
        SET _ok=1
    )
)
IF %_index% EQU 0 SET _exit=100&& GOTO R01_STEP5
ECHO:
ECHO:  99. Exit

REM Get user input.
:R01_STEP2
ECHO:
ECHO:
SET /P _answer="Please choose environment: "

REM Check user input.
:R01_STEP3
SET _ko=
FOR /F "usebackq delims=0123456789" %%A IN ('%_answer%') DO SET _ko=%%A
IF DEFINED _ko GOTO R01_STEP1
IF NOT DEFINED _ko IF %_answer% EQU 99 SET _exit=100&& GOTO R01_STEP5
IF NOT DEFINED _ko IF %_answer% GTR %_index% GOTO R01_STEP1

REM Get virtual environment respective directory.
:R01_STEP4
SET _name=!_dir%_answer%!
IF %_answer% LEQ 9 SET _name=!_dir0%_answer%!
SET _venv=%_myparent%MyPythonProject\VirtualEnv\%_name%\Scripts

:R01_STEP5
(
    POPD
    ENDLOCAL
    SET _name=%_name%
    SET _venv=%_venv%
    EXIT /B %_exit%
)


REM python %_myparent%MyPythonProject\AudioCD\DigitalAudioFiles`View.py
REM IF NOT ERRORLEVEL 1 (
    REM IF EXIST "%_xmldigitalaudiobase%" (
        REM java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        REM DEL "%_xmldigitalaudiobase%"
    REM )
REM )
REM GOTO MENU
