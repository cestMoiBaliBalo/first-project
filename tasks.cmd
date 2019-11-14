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
SET _cloud_avchd=\\DISKSTATION\backup\AVCHD Vidéos
SET _cp=1252
SET _echo=0
SET _local_avchd=G:\Videos\AVCHD Videos
SET _exclusions=%_RESOURCES%\exclusions1.txt
SET _xxcopy=xxcopy.cmd


REM ============
REM Main script.
REM ============
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


REM ===========================
REM Set ECHO on for debug mode.
REM ===========================
IF /I ["%~1"] EQU ["DEBUG"] (
    @ECHO on
    @SET _echo=1
)


REM -------------
REM Display menu.
REM -------------
:MENU
python %_PYTHONPROJECT%\Tasks\Manager\main.py


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM -----------------------------------------
REM Sync PDF documents to local CloudStation.
REM -----------------------------------------
IF ERRORLEVEL 36 (
    CLS
    CALL %_COMPUTING%\start.cmd 9
    GOTO MENU
)


REM -----------------------
REM Audio tables interface.
REM -----------------------
IF ERRORLEVEL 35 (
    PUSHD "%_PYTHONPROJECT%\GUI\Sources\03"
    python main.py
    POPD
    GOTO MENU
)


REM --------------------------
REM Backup files to USB drive.
REM --------------------------
IF ERRORLEVEL 34 (
    CLS
    "C:/Program Files/Areca/areca_cl.exe" backup -f -c -wdir "%TEMP%\tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg"
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


IF ERRORLEVEL 33 (
:STEP_33
    CLS
    TYPE %_RESOURCES%\digital_bootlegs_audiotags_bs.txt
    ECHO:
    ECHO:
    ECHO:
    SET /P _answer=Enter requested action number: 
    IF [!_answer!] EQU [99] GOTO MENU
    IF [!_answer!] EQU [2] (
        IF EXIST %TEMP%\%_xxcopy% (
            CLS
            TYPE %TEMP%\%_xxcopy%
            ECHO:
            ECHO:
            PAUSE
        )
        GOTO STEP_33
    )
    IF [!_answer!] EQU [1] (
        IF EXIST %TEMP%\%_xxcopy% (
            CLS
            CALL %TEMP%\%_xxcopy%
            ECHO:
            ECHO:
            PAUSE
        )
        GOTO STEP_33
    )
)


IF ERRORLEVEL 32 (
    SET _commandsfile=rippedtracks.cmd
    SET _tracksfile=rippedtracks.txt
    IF EXIST "\\diskstation\music" (
        PUSHD %_RESOURCES%
        IF EXIST !_commandsfile! (
            CLS
            CALL !_commandsfile! 0 && DEL !_commandsfile! && DEL !_tracksfile! 2> NUL
            ECHO:
            ECHO:
            PAUSE
        )
        POPD
    )
    SET _commandsfile=
    SET _tracksfile=
    GOTO MENU
)


REM --------------------------------------
REM Update Audio database with new albums.
REM --------------------------------------
IF ERRORLEVEL 31 (
    PUSHD "%TEMP%"
    python -m Applications.Tables.Albums.main trackslist.txt --encoding UTF_16
    POPD
    GOTO MENU
)


REM --------------------------------
REM Update audio albums played date.
REM --------------------------------
IF ERRORLEVEL 30 (
    PUSHD "%_PYTHONPROJECT%\GUI\Sources\06"
    python main.py
    POPD
    GOTO MENU
)


REM ------------------------------------
REM Python arguments parsers unit tests.
REM ------------------------------------
IF ERRORLEVEL 29 (
    CLS
    ECHO:
    python -m unittest -v Applications.Unittests.module2
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ------------------------
REM Additional backup tasks.
REM ------------------------
IF ERRORLEVEL 28 (
    SET _error=0

:TARGETS
    CLS
    SET _answer=
    SET _target=
    PUSHD %_RESOURCES%
    TYPE backup_menu.txt
    SET /P _answer= || GOTO TARGETS
    IF [!_answer!] EQU [99] (
        POPD
        GOTO END_TARGETS
    )
    FOR /F "usebackq delims=| tokens=1,2" %%I IN ("backup_targets.txt") DO IF [%%I] EQU [!_answer!] SET _target=%%J
    IF NOT DEFINED _target (
        POPD
        SET /A "_error+=1"
        GOTO TARGETS
    )
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music !_target!
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    POPD
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO TARGETS

:END_TARGETS
    SET _answer=
    SET _error=
    SET _target=
    GOTO MENU

)


REM ----------------------------------------
REM Backup personal files to SD memory card.
REM ----------------------------------------
IF ERRORLEVEL 24 (
    CLS
    PUSHD "%TEMP%"
    DEL %_xxcopy% 2> NUL
    python "%_PYTHON_SECONDPROJECT%\backup.py"
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        PAUSE
        POPD
        GOTO MENU
    )
    IF EXIST "%_xxcopy%" CALL "%_xxcopy%"
    ECHO:
    ECHO:
    PAUSE
    POPD
    GOTO MENU
)


REM -------------------------------------------------------------------
REM Clone "\\DISKSTATION\backup\Images\Collection" to local collection.
REM -------------------------------------------------------------------
IF ERRORLEVEL 23 (
    CLS

:MENU23
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy images from MyCloud to local drive H." _answer
    IF [!_answer!] EQU [N] GOTO FIN23

    REM -->  1. Check if new files have been inserted since the previous sync.
    CLS
    XXCOPY "\\DISKSTATION\backup\Images\Collection\*\?*\*.jpg" "H:\" /L /ZS /Q3 /CLONE /Z0 /oA:%_XXCOPYLOG%
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        ECHO No new files inserted: syncing is not required. Task is going to end.
        ECHO:
        ECHO:
        PAUSE
        GOTO FIN23
    )

    REM -->  2. Clone "\\DISKSTATION\Images\Collection" to local drive H. Don't delete extra files and directories!
    CLS
    XXCOPY /EC "\\DISKSTATION\backup\Images\Collection\*\?*\*.jpg" "H:\" /CLONE /Z0 /oA:%_XXCOPYLOG%

    REM -->  3. Then pause.
    ECHO:
    ECHO:
    PAUSE

    REM -->  4. Reverse both source and destination. Then remove brand new files in order to preserve some folders content.
    REM         - "RECYCLER".
    REM         - "$RECYCLE.BIN".
    REM         - "SYSTEM VOLUME INFORMATION".
    REM         - "IPHONE".
    REM         - "RECOVER".
    CLS
    XXCOPY /CE "H:\" "\\DISKSTATION\backup\Images\Collection\" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%

    REM -->  5. Then pause.
    ECHO:
    ECHO:
    PAUSE

:FIN23
    GOTO MENU

)


IF ERRORLEVEL 22 (
    CLS
    ECHO:
    PUSHD %_PYTHONPROJECT%
    python textrunner.py
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


IF ERRORLEVEL 21 (
    CLS
    ECHO:
    python -m unittest -v Applications.Unittests.module5
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


IF ERRORLEVEL 20 (
    SET _command=python -m unittest -v
    FOR /F "usebackq" %%A IN ("%_RESOURCES%\unittests2.txt") DO SET _command=!_command! %%A
    CLS
    ECHO:
    !_command!
    ECHO:
    ECHO:
    PAUSE
    SET _command=
    GOTO MENU
)


IF ERRORLEVEL 19 (
    SET _command=python -m unittest -v
    FOR /F "usebackq" %%A IN ("%_RESOURCES%\unittests1.txt") DO SET _command=!_command! %%A
    CLS
    ECHO:
    !_command!
    ECHO:
    ECHO:
    PAUSE
    SET _command=
    GOTO MENU
)


REM -------------------
REM MyCloud video sync.
REM -------------------
REM Delete extra files.
IF ERRORLEVEL 18 (
    GOTO MENU
    CLS

:MENU18
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy local Hi-Res video files to MyCloud." _answer
    IF [!_answer!] EQU [N] GOTO FIN18
    CLS
    XXCOPY /EC "%_local_avchd%\?*\*.mts" "%_cloud_avchd%\" /BI /FF /KS /Y /oA:%_XXCOPYLOG%
    XXCOPY /CE "%_local_avchd%\?*\*.m2ts" "%_cloud_avchd%\" /BI /FF /KS /Y /oA:%_XXCOPYLOG%
    XXCOPY /CE "%_cloud_avchd%\" "%_local_avchd%\" /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:FIN18
    GOTO MENU

)


REM -------------------
REM MyCloud audio sync.
REM -------------------
IF ERRORLEVEL 17 (
    CLS
    PUSHD %TEMP% 
    DEL %_xxcopy% 2> NUL
    python "%_PYTHONPROJECT%\GUI\Sources\01\main.py" --repository MyCloud
    IF NOT ERRORLEVEL 1 CALL :TOTO
    POPD
    GOTO MENU
)


REM --------------------------------------------------
REM Sync mobile devices from local audio repositories.
REM --------------------------------------------------
IF ERRORLEVEL 16 (
    CLS
    PUSHD %TEMP% 
    DEL %_xxcopy% 2> NUL
    python "%_PYTHONPROJECT%\GUI\Sources\02\main.py"
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        POPD
        GOTO MENU
    )
    IF EXIST "%_xxcopy%" CALL "%_xxcopy%"
    ECHO:
    ECHO:
    PAUSE
    POPD
    GOTO MENU
)


REM ----------------
REM Images renaming.
REM ----------------
IF ERRORLEVEL 15 GOTO P01


REM ------------------------------
REM Sync local audio repositories.
REM ------------------------------
IF ERRORLEVEL 13 (
    CLS
    PUSHD %TEMP% 
    DEL %_xxcopy% 2> NUL
    python "%_PYTHONPROJECT%\GUI\Sources\01\main.py"
    IF NOT ERRORLEVEL 1 CALL :TOTO
    POPD
    GOTO MENU
)
REM python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
REM IF NOT ERRORLEVEL 1 (
    REM IF EXIST "%_xmldigitalaudiobase%" (
        REM java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        REM DEL "%_xmldigitalaudiobase%"
    REM )
REM )
REM GOTO MENU


IF ERRORLEVEL 12 (
    CLS
    ECHO:
    python -m unittest -v Applications.Unittests.module4
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)

REM -------------------------------
REM Python installed packages list.
REM -------------------------------
IF ERRORLEVEL 11 (
    CLS
    pip list
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ------------------------------
REM Python outdated packages list.
REM ------------------------------
IF ERRORLEVEL 10 (
    CLS
    pip list -o
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ------------
REM Upgrade pip.
REM ------------
IF ERRORLEVEL 9 (
    CLS
    python -m pip install --upgrade pip
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM -------------------------------------
REM Toggle to python virtual environment.
REM -------------------------------------
IF ERRORLEVEL 8 (
    CLS
    SET /P _answer=Please enter virtual environment name: 
    IF EXIST "%_PYTHONPROJECT%\VirtualEnv\!_answer!" (
        CALL "%_COMPUTING%\environment.cmd" A !_answer!
        CMD /K PROMPT [!_answer! environment]$G
        CALL "%_COMPUTING%\environment.cmd" D
    )
    GOTO MENU
)


REM --------------
REM Artists [U-Z].
REM --------------
IF ERRORLEVEL 6 (
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 204959095
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM --------------
REM Artists [P-T].
REM --------------
IF ERRORLEVEL 5 (
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 1535780732
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM --------------
REM Artists [K-O].
REM --------------
IF ERRORLEVEL 4 (
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 1196865155
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM --------------
REM Artists [F-J].
REM --------------
IF ERRORLEVEL 3 (
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 1674209532
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM --------------
REM Artists [A-E].
REM --------------
IF ERRORLEVEL 2 (
    CLS
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 854796030
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    CALL "%_COMPUTING%\environment.cmd" A venv36
    PUSHD %_PYTHONPROJECT%\Backup
    python backup.py -c music 854796030 1674209532 1196865155 1535780732 204959095
    POPD
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO MENU
)


REM ==========
REM Exit menu.
REM ==========
:EXIT
CLS
EXIT /B 0


REM ===================================
REM Specific parts for renaming images.
REM ===================================
:P01
rem PUSHD %_PYTHONPROJECT%
rem python some_interface.py
rem IF ERRORLEVEL 1 (
rem     SET _argument=%ERRORLEVEL%
rem     GOTO P01A
rem )
rem IF ERRORLEVEL 0 (
rem     POPD
rem     GOTO MENU
rem )
SET _argument=2018


:P01A
CALL %_RESOURCES%\images.cmd %_argument%
IF ERRORLEVEL 11 GOTO MENU
IF ERRORLEVEL 10 GOTO P01A


:QUESTION
SET %5=Y
ECHO:
ECHO:
CHOICE /C %~1 /T %~2 /N /D %~3 /M "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET %5=N
EXIT /B 0


:TOTO
PUSHD "%TEMP%"
IF EXIST "%_xxcopy%" (
    CLS
    ECHO The following XXCOPY commands will be run:
    ECHO:
    ECHO:
    FOR /F "usebackq delims=. tokens=1,*" %%I IN ("%_xxcopy%") DO IF [%%I] EQU [XXCOPY] CALL ECHO %%I.%%J
    ECHO:
    ECHO:
    CALL :QUESTION "YN" "90" "N" "Would you like to continue? " _answer
    IF [!_answer!] EQU [Y] (
        CLS
        CALL "%_xxcopy%"
        ECHO:
        ECHO:
        PAUSE
    )
)
POPD
EXIT /B 0
