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
SET _local_avchd=G:\Videos\AVCHD Videos
SET _xxcopy=xxcopy.cmd


REM ============
REM Main script.
REM ============
FOR /F "usebackq tokens=2 delims=:" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp% > NUL


REM ===========================
REM Set ECHO on for debug mode.
REM ===========================
IF /I ["%~1"] EQU ["DEBUG"] @ECHO on


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
    PUSHD "%_PYTHONPROJECT%\Interfaces\Sources\03"
    python main.py
    POPD
    GOTO MENU
)


REM --------------------------
REM Backup files to USB drive.
REM --------------------------
IF ERRORLEVEL 34 (
    CLS
    "C:/Program Files/Areca/areca_cl.exe" backup -f -c -wdir "%TEMP%/tmp-Xavier" -config "%_BACKUP%/workspace.documents/34258241.bcfg"
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


REM -------------------------------
REM Update audio discs played date.
REM -------------------------------
IF ERRORLEVEL 30 (
    PUSHD "%_PYTHONPROJECT%\Interfaces\Sources\06"
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


REM ---------------------------------------
REM Clone personal files to SD memory card.
REM ---------------------------------------
IF ERRORLEVEL 24 (
    CLS
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


REM --------------------
REM Sync MyCloud videos.
REM --------------------
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


REM -------------------
REM sync MyCloud audio.
REM -------------------
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

:STEP8A
    PUSHD %_PYTHONPROJECT%\Tasks
    python virtualenv.py
    IF ERRORLEVEL 100 GOTO STEP8D

:STEP8B
    CLS
    IF NOT EXIST %_TMPTXT% GOTO STEP8D
    SET _venv=
    SET _choice=
    SET _length=0

    REM Display menu.
    ECHO:
    ECHO Available virtual environment(s^):
    ECHO:
    FOR /F "usebackq tokens=1,2 delims=|" %%A IN ("%_TMPTXT%") DO (
        SET /A "_length+=1"
        IF %%A LEQ 9 ECHO:  %%A. %%B
        IF %%A GTR 9 IF %%A LSS 99 ECHO: %%A. %%B
        IF %%A EQU 99 ECHO: && ECHO: %%A. %%B
    )
    SET /A "_length-=1"
    ECHO:
    ECHO:
    SET /P _answer=Please choose an environment: || GOTO STEP8B

    REM Check user input.
    FOR /F "usebackq delims=0123456789" %%A IN ('!_answer!') DO SET _choice=%%A
    IF DEFINED _choice GOTO STEP8B
    IF NOT DEFINED _choice IF !_answer! EQU 99 GOTO STEP8C
    IF NOT DEFINED _choice IF !_answer! GTR !_length! GOTO STEP8B

    REM Get virtual environment name.
    FOR /F "usebackq tokens=1,2 delims=|" %%A IN ("%_TMPTXT%") DO IF %%A EQU !_answer! SET _venv=%%B

    REM Set virtual environment.
    IF NOT DEFINED _venv GOTO STEP8C
    IF NOT EXIST "%_PYTHONPROJECT%\VirtualEnv\!_venv!" GOTO STEP8C
    CLS
    CALL "%_COMPUTING%\environment.cmd" A !_venv!
    CMD /K PROMPT [!_venv! environment]$G

    REM Restore previous environment.
    CALL "%_COMPUTING%\environment.cmd" D
    GOTO STEP8B

:STEP8C
    SET _venv=
    SET _choice=
    SET _length=

:STEP8D
    REM Use delayed expansion here because global variable PATH contains a path with parenthesis.
    REM Because they are embedded into a parenthesis block the internal parenthesis counter is faked
    REM and leads to a fatal error.
    PUSHD ..
    SET _path=!PATH!
    SET path=%_PYTHONPROJECT%\VirtualEnv\venv38;!PATH!
    python temporaryenv.py > NUL
    SET path=!_path!
    SET _path=
    POPD
    POPD
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


REM ----------------------
REM Backup artists  [P-T].
REM ----------------------
IF ERRORLEVEL 5 (
    CLS
    CALL :BACKUP 1535780732
    GOTO MENU
)


REM ----------------------
REM Backup artists  [K-O].
REM ----------------------
IF ERRORLEVEL 4 (
    CLS
    CALL :BACKUP 1196865155
    GOTO MENU
)


REM ----------------------
REM Backup artists  [F-J].
REM ----------------------
IF ERRORLEVEL 3 (
    CLS
    CALL :BACKUP 1674209532
    GOTO MENU
)


REM ----------------------
REM Backup artists  [A-E].
REM ----------------------
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


:BACKUP
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _arguments=
SET _output=%TEMP%\backup.txt

@REM -----
DEL %_output% 2> NUL

@REM -----
PUSHD %_COMPUTING%\MyJavaProject

@REM    ----------
@REM A. Java step.
@REM    ----------
@REM    Enumerate files.
:STEP1
IF [%~1] EQU [] GOTO STEP2
SET _arguments=%_arguments% %~1

@REM -----
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

@REM    ------------
@REM B. Python step.
@REM    ------------
@REM    Check if backup is required.
:STEP2
IF NOT EXIST %_output% GOTO STEP4

@REM ----- B.1. Define 3.8 as python interpreter.
SET _path=%PATH%
SET PATH=%_PYTHONPROJECT%\VirtualEnv\venv38;%PATH%
ECHO: PATH is composed of the following folders.
ECHO:
CALL :GET_PATHS "%PATH%"
ECHO:
ECHO:
PAUSE
CLS

@REM ----- B.2. Run checker.
PUSHD ..\MyPythonProject\Backup
python check.py "%_output%" "\.(?:ape|dsf|flac)$" --pprint

@REM ----- B.3. Backup isn't required.
IF ERRORLEVEL 100 (
    POPD
    ECHO:
    ECHO:
    PAUSE
    CLS
    GOTO STEP3
)

@REM ----- B.4. Backup is required.
CHOICE /C YN /N /CS /T 30 /D N /M "An additional backup is required. Would you like to run it? [Y/N] "

@REM ----- Backup is aborted.
IF ERRORLEVEL 2 (
    CLS
    GOTO STEP3
)

@REM ----- B.5. Backup is run.
CLS
ECHO: The following backup command will be run: python main.py -c music%_arguments%
CHOICE /C YN /N /CS /T 30 /D N /M "Would you like to continue? [Y/N] "
IF ERRORLEVEL 2 (
    POPD
    CLS
    GOTO STEP3
)
python main.py -c music%_arguments%
POPD
ECHO:
ECHO:
PAUSE
ECHO:
ECHO:

@REM    ---------------
@REM C. End of routine.
@REM    ---------------

@REM -----
:STEP3
SET path=%_path%
SET _path=
ECHO: PATH is now composed of the following folders.
ECHO:
CALL :GET_PATHS "%PATH%"
ECHO:
ECHO:
PAUSE
CLS

@REM -----
:STEP4
SET _arguments=
SET _environment=
SET _output=
SET _path=
SET _regex=
SET _target=
POPD
ENDLOCAL
EXIT /B 0


:GET_PATHS
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _index=0
SET _path=%~1
:LOOP
FOR /F "usebackq tokens=1* delims=;" %%A IN ('!_path!') DO (
    SET /A "_index+=1"
    IF !_index! LEQ 9 ECHO    !_index!. %%A
    IF !_index! GTR 9 IF !_index! LEQ 99 ECHO   !_index!. %%A
    IF !_index! GTR 99 IF !_index! LEQ 999 ECHO  !_index!. %%A
    SET _path=%%B
    GOTO LOOP
)
SET _path=
ENDLOCAL
EXIT /B 0


REM python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
REM IF NOT ERRORLEVEL 1 (
    REM IF EXIST "%_xmldigitalaudiobase%" (
        REM java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        REM DEL "%_xmldigitalaudiobase%"
    REM )
REM )
REM GOTO MENU
