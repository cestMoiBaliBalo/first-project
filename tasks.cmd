@ECHO off


REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"


SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _cloud_avchd=\\DISKSTATION\backup\AVCHD Vidéos
SET _local_avchd=G:\Videos\AVCHD Videos
SET _xxcopy=xxcopy.cmd
SET _cp=1252


REM ============
REM Main script.
REM ============
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


REM ===========================
REM Set ECHO ON for debug mode.
REM ===========================
IF /I "%~1" EQU "DEBUG" @ECHO on


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
    PUSHD %_myparent%
    CALL start.cmd 9
    POPD
    GOTO MENU
)


REM -----------------------
REM Audio tables interface.
REM -----------------------
IF ERRORLEVEL 35 (
    PUSHD "%_PYTHONPROJECT%\Interfaces\Sources\03"
    python main.py
    POPD
    GOTO MENU
)


REM --------------------------
REM Sync targets repositories.
REM --------------------------
IF ERRORLEVEL 34 (
    SETLOCAL ENABLEDELAYEDEXPANSION
    SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;!PATH!
    PUSHD %_PYTHONPROJECT%\Backup
    python targets.py %_BACKUP%\workspace.music
    POPD
    ENDLOCAL
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


REM ---------------------------------
REM Insert audio discs into database.
REM ---------------------------------
IF ERRORLEVEL 31 (
    PUSHD %TEMP%
    python -m Applications.Tables.Albums.main trackslist.txt --encoding UTF_16
    POPD
    GOTO MENU
)


REM -------------------------------
REM Update audio discs played date.
REM -------------------------------
IF ERRORLEVEL 30 (
    PUSHD %_PYTHONPROJECT%\Interfaces\Sources\06
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
    FOR /F "usebackq tokens=1,2 delims=|" %%I IN ("backup_targets.txt") DO IF [%%I] EQU [!_answer!] SET _target=%%J
    IF NOT DEFINED _target (
        POPD
        GOTO TARGETS
    )
    CLS
    CALL :BACKUP !_target!
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO TARGETS

:END_TARGETS
    SET _answer=
    SET _target=
    GOTO MENU

)


REM ----------------------------------------
REM Copy HDtracks.com files to backup drive.
REM ----------------------------------------
IF ERRORLEVEL 27 (
    CLS
    IF EXIST z: (
        XXCOPY /EC %_MYMUSIC%\HDtracks\ z:\HDtracks\ /S /KS /RCY /PD0 /ED1 /oF3 /Fo%TEMP%\FileList /oA%_XXCOPYLOG%
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
    PUSHD %_myparent%
    CALL lossy.cmd P
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
    XXCOPY /EC "\\DISKSTATION\backup\Images\Collection\*\?*\*.jpg" "H:\" /L /ZS /Q3 /CLONE /Z0 /oA:%_XXCOPYLOG%
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

    REM -->  4. Reverse both source and destination. Then remove brand new files in order to preserve specific folders content.
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


REM --------------------------
REM Run all python unit tests.
REM --------------------------
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


REM -----------------------------------------
REM Run python ripped audio discs unit tests.
REM -----------------------------------------
IF ERRORLEVEL 21 (
    CLS
    ECHO:
    python -m unittest -v Applications.Unittests.module5
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ------------------------------------------
REM Run python regular expressions unit tests.
REM ------------------------------------------
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


REM ------------------------------------------------
REM Run python data validation functions unit tests.
REM ------------------------------------------------
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


REM -------------------------
REM Sync MyCloud video files.
REM -------------------------
REM Delete extra files.
IF ERRORLEVEL 18 (
    GOTO FIN18
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


REM -------------------------
REM Sync MyCloud audio files.
REM -------------------------
IF ERRORLEVEL 17 (
    CLS
    PUSHD %TEMP%
    DEL %_xxcopy% 2> NUL
    python "%_PYTHONPROJECT%\Interfaces\Sources\01\main.py" --repository MyCloud
    IF NOT ERRORLEVEL 1 CALL :CONFIRM
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
    python "%_PYTHONPROJECT%\Interfaces\Sources\02\main.py"
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


REM ------------------------------
REM Sync local audio repositories.
REM ------------------------------
IF ERRORLEVEL 13 (
    CLS
    PUSHD %TEMP%
    DEL %_xxcopy% 2> NUL
    python "%_PYTHONPROJECT%\Interfaces\Sources\01\main.py"
    IF NOT ERRORLEVEL 1 CALL :CONFIRM
    POPD
    GOTO MENU
)


REM ------------------------------------------------------
REM Run python audio discs ripping application unit tests.
REM ------------------------------------------------------
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
REM List python installed packages.
REM -------------------------------
IF ERRORLEVEL 11 (
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
    GOTO MENU
)


REM ------------------------------
REM List Python outdated packages.
REM ------------------------------
IF ERRORLEVEL 10 (
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
    GOTO MENU
)


REM ------------
REM Upgrade pip.
REM ------------
IF ERRORLEVEL 9 (
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
    GOTO MENU
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
    CALL "%_COMPUTING%\environment.cmd" A !_name!
    CMD /K PROMPT [!_name! environment]$G
    CALL "%_COMPUTING%\environment.cmd" D
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
    CLS
    CALL :BACKUP 204959095
    GOTO MENU
)


REM ---------------------
REM Backup artists [P-T].
REM ---------------------
IF ERRORLEVEL 5 (
    CLS
    CALL :BACKUP 1535780732
    GOTO MENU
)


REM ---------------------
REM Backup artists [K-O].
REM ---------------------
IF ERRORLEVEL 4 (
    CLS
    CALL :BACKUP 1196865155
    GOTO MENU
)


REM ---------------------
REM Backup artists [F-J].
REM ---------------------
IF ERRORLEVEL 3 (
    CLS
    CALL :BACKUP 1674209532
    GOTO MENU
)


REM ---------------------
REM Backup artists [A-E].
REM ---------------------
IF ERRORLEVEL 2 (
    CLS
    CALL :BACKUP 854796030
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    CLS
    CALL :BACKUP 854796030 1674209532 1196865155 1535780732 204959095
    GOTO MENU
)


REM ==========
REM Exit menu.
REM ==========
:EXIT
CLS
EXIT /B 0


REM ================
REM Local functions.
REM ================


:QUESTION
SET %5=Y
ECHO:
ECHO:
CHOICE /C %~1 /T %~2 /N /D %~3 /M "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET %5=N
EXIT /B 0


:CONFIRM
PUSHD "%TEMP%"
IF EXIST "%_xxcopy%" (
    CLS
    ECHO The following XXCOPY commands will be run:
    ECHO:
    ECHO:
    FOR /F "usebackq tokens=1,* delims=." %%I IN ("%_xxcopy%") DO IF [%%I] EQU [XXCOPY] CALL ECHO %%I.%%J
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


REM ===================
REM BACKUP AUDIO FILES.
REM ===================
REM Check at first if backup is required then backup if confirmed by user interface.
:BACKUP
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _arguments=
SET _output=%TEMP%\backup.txt
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38\Scripts;%PATH%

REM -----
DEL %_output% 2> NUL

REM -----
PUSHD %_COMPUTING%\MyJavaProject

REM    ----------
REM A. Java step.
REM    ----------
REM    Enumerate files.
:STEP1
IF [%~1] EQU [] GOTO STEP2
SET _arguments=%_arguments% %~1

REM -----
FOR /F "usebackq eol=# tokens=1-4 delims=`" %%A IN ("targets.txt") DO (
    IF [%%~A] EQU [%~1] (
        SET _target=%%~A
        SET _environment=%%~B
        SET _path=%%~C
        SET _regex=%%~D
        SET _command="!_path!" "!_target!" "!_environment!" --output "%_output%"
        IF DEFINED _regex SET _command=!_command! --regex "!_regex!"
        PUSHD out\production\MyJavaProject
        java com.xavier.computing.Finder !_command! > NUL
        POPD
    )
)
SHIFT /1
GOTO STEP1

REM    ------------
REM B. Python step.
REM    ------------
REM    Check if backup is required.
:STEP2
IF NOT EXIST %_output% GOTO STEP4

REM ----- B.1. Define 3.8 as python interpreter.
ECHO: PATH is composed of the following directories.
ECHO:
CALL :GET_PATHS
ECHO:
ECHO:
PAUSE
CLS

REM ----- B.2. Run checker.
PUSHD ..\MyPythonProject\Backup
python check.py "%_output%" "\.(?:ape|dsf|flac)$" --pprint

REM ----- B.3. Backup isn't required.
IF ERRORLEVEL 100 (
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO STEP3
)

REM ----- B.4. Backup is required.
ECHO:
CHOICE /C YN /N /CS /T 30 /D N /M "An additional backup is required. Would you like to run it? Press [Y] for Yes or [N] for No. "
CLS

REM ----- Backup is aborted.
IF ERRORLEVEL 2 (
    POPD
    GOTO STEP3
)

REM ----- B.5. Backup is run.
ECHO The following backup command will be run: python main.py -c music%_arguments%
ECHO:
CHOICE /C YN /N /CS /T 30 /D N /M "Would you like to continue? Press [Y] for Yes or [N] for No. "
IF ERRORLEVEL 2 (
    POPD
    GOTO STEP3
)
python main.py -c music%_arguments%
POPD
ECHO:
ECHO:
PAUSE
ECHO:
ECHO:

REM    ----------------
REM C. End of function.
REM    ----------------

REM -----
:STEP3
CLS
POPD
(
    ENDLOCAL
    ECHO: PATH is now composed of the following folders.
    ECHO:
    CALL :GET_PATHS
    ECHO:
    ECHO:
    PAUSE
    CLS
    EXIT /B 0
)

REM -----
:STEP4
CLS
POPD
(
    ENDLOCAL
    ECHO:
    ECHO:
    PAUSE
    CLS
    EXIT /B 0
)


REM =====================================
REM GET THE LIST OF PATHS COMPOSING PATH.
REM =====================================
:GET_PATHS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _index=0
SET _path=%PATH%
:R04_LOOP
FOR /F "usebackq tokens=1* delims=;" %%A IN ('!_path!') DO (
    SET /A "_index+=1"
    IF !_index! LEQ 9 ECHO    !_index!. %%A
    IF !_index! GTR 9 IF !_index! LEQ 99 ECHO   !_index!. %%A
    IF !_index! GTR 99 IF !_index! LEQ 999 ECHO  !_index!. %%A
    SET _path=%%B
    GOTO R04_LOOP
)
ENDLOCAL
EXIT /B 0


REM ===============================================
REM GET THE LIST OF AVAILABLE VIRTUAL ENVIRONMENTS.
REM ===============================================
:GET_VIRTUALENV
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _index=0
SET _exit=0
SET _name=
SET _venv=
PUSHD %_PYTHONPROJECT%\VirtualEnv

:R05_STEP1
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
IF %_index% EQU 0 SET _exit=100&& GOTO R05_STEP5
ECHO:
ECHO:  99. Exit

REM Get user input.
:R05_STEP2
ECHO:
ECHO:
SET /P _answer="Please choose environment: "

REM Check user input.
:R05_STEP3
SET _ko=
FOR /F "usebackq delims=0123456789" %%A IN ('%_answer%') DO SET _ko=%%A
IF DEFINED _ko GOTO R05_STEP1
IF NOT DEFINED _ko IF %_answer% EQU 99 SET _exit=100&& GOTO R05_STEP5
IF NOT DEFINED _ko IF %_answer% GTR %_index% GOTO R05_STEP1

REM Get virtual environment respective directory.
:R05_STEP4
SET _name=!_dir%_answer%!
IF %_answer% LEQ 9 SET _name=!_dir0%_answer%!
SET _venv=%_PYTHONPROJECT%\VirtualEnv\%_name%\Scripts

:R05_STEP5
POPD
(
    ENDLOCAL
    SET _name=%_name%
    SET _venv=%_venv%
    EXIT /B %_exit%
)


REM python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
REM IF NOT ERRORLEVEL 1 (
    REM IF EXIST "%_xmldigitalaudiobase%" (
        REM java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        REM DEL "%_xmldigitalaudiobase%"
    REM )
REM )
REM GOTO MENU
