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
FOR /F "usebackq delims=: tokens=2" %%I IN (`CHCP`) DO FOR /F "usebackq" %%J IN ('%%I') DO IF %%J NEQ %_cp% CHCP %_cp%


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


REM ----------------------------------------
REM Springsteen 200* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 28 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1222562470
    POPD
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2009 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 27 (
    CLS
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1068554868
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 201* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 26 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1306312508
    POPD
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2016 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 25 (
    CLS
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1066663185
    POPD
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ----------------------------------------
REM Backup personal files to SD Memory Card.
REM ----------------------------------------
IF ERRORLEVEL 24 (
    CLS
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD %_PYTHON_SECONDPROJECT%
    python backup.py
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        PAUSE
        POPD
        GOTO MENU
    )
    PUSHD "%TEMP%"
    IF EXIST "%_xxcopy%" CALL "%_xxcopy%"
    ECHO:
    ECHO:
    PAUSE
    POPD
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


REM ------------------------
REM MyCloud full video sync.
REM ------------------------
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


REM ------------------------
REM MyCloud full audio sync.
REM ------------------------
REM Delete extra files.
IF ERRORLEVEL 17 (
    GOTO MENU
    CLS

:MENU17
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy local FLAC audio files to MyCloud." _answer
    IF [!_answer!] EQU [N] GOTO FIN18
    CLS
    XXCOPY "F:\*\?*\*.flac" "\\DISKSTATION\music\" /EX:"%_exclusions%" /CLONE /PZ0 /Fo:"%_COMPUTING%\Log\copied_/$YMMDD_K_HHNNSS$.lst" /FM:L /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:FIN17
    GOTO MENU

)


REM --------------------------------------------------
REM Sync mobile devices from local audio repositories.
REM --------------------------------------------------
IF ERRORLEVEL 16 (
    CLS
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD "%_PYTHONPROJECT%\GUI\Sources\02"
    python main.py
    IF ERRORLEVEL 1 (
        ECHO:
        ECHO:
        PAUSE
        POPD
        GOTO MENU
    )
    PUSHD "%TEMP%"
    IF EXIST "%_xxcopy%" CALL "%_xxcopy%"
    ECHO:
    ECHO:
    PAUSE
    POPD
    POPD
    GOTO MENU
)


REM ----------------
REM Images renaming.
REM ----------------
IF ERRORLEVEL 15 GOTO P01


REM ---------------------------
REM MyCloud partial audio sync.
REM ---------------------------
IF ERRORLEVEL 14 GOTO MENU


REM ------------------------------
REM Sync local audio repositories.
REM ------------------------------
IF ERRORLEVEL 13 (
    CLS
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD "%_PYTHONPROJECT%\GUI\Sources\01"
    python main.py
    IF !ERRORLEVEL! EQU 0 (
        PUSHD "%TEMP%"
        IF EXIST "%_xxcopy%" (
            CALL "%_xxcopy%"
            ECHO:
            ECHO:
            PAUSE
        )
        POPD
    )
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


REM -----------------------
REM Display folder content.
REM -----------------------
REM IF ERRORLEVEL 10 (
REM     PUSHD "%_PYTHONPROJECT%\Tasks\03"
REM     python main.py
REM     POPD
REM     GOTO MENU

REM )


REM -----------------------
REM Update python packages.
REM -----------------------
IF ERRORLEVEL 9 (
    REM CLS
    REM pip install -U --upgrade-strategy="only-if-needed" -r "%_COMPUTING%\pip-commands.txt"
    REM ECHO:
    REM ECHO:
    REM PAUSE
    GOTO MENU
)


REM -----------------------------------------
REM Bruce Springsteen bootlegs series backup.
REM -----------------------------------------
IF ERRORLEVEL 8 (
    GOTO MENU
)


REM ---------------------------------
REM Pearl Jam bootlegs series backup.
REM ---------------------------------
IF ERRORLEVEL 7 (
    GOTO MENU
)


REM --------------
REM Artists [U-Z].
REM --------------
IF ERRORLEVEL 6 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 204959095
    POPD
    GOTO MENU
)


REM --------------
REM Artists [P-T].
REM --------------
IF ERRORLEVEL 5 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1535780732
    POPD
    GOTO MENU
)


REM --------------
REM Artists [K-O].
REM --------------
IF ERRORLEVEL 4 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1196865155
    POPD
    GOTO MENU
)


REM --------------
REM Artists [F-J].
REM --------------
IF ERRORLEVEL 3 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1674209532
    POPD
    GOTO MENU
)


REM --------------
REM Artists [A-E].
REM --------------
IF ERRORLEVEL 2 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 854796030
    POPD
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    PUSHD "G:\Computing\MyPythonProject\venv36\Scripts"
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 854796030 1674209532 1196865155 1535780732 204959095
    POPD
    GOTO MENU
)


REM ==========
REM Exit menu.
REM ==========
:EXIT
CLS
EXIT /B 0


REM ==============================================================
REM Specific parts for partially syncing MyCloud with audio files.
REM ==============================================================


:P00
SET _tempvar=
CALL:HEADER2
ECHO:
ECHO:
ECHO: Available options:
ECHO:
ECHO:  1. By parent folder (default^).
ECHO:  2. By artist folder.
ECHO:
ECHO:
SET /P _choice=Please choose an option or press ENTER to choose the default option: || SET _choice=1

REM 1. %_choice% must be an integer number.
FOR /F "tokens=* delims=12" %%A IN ("%_choice%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO P00

REM 3. Go to the respective script.
SET _chosenopt=%_choice%
GOTO P0

:END_P00
GOTO MENU


:P0
SET _key=
SET _choice=
SET _difference=
CALL:HEADER2
ECHO:
IF %_chosenopt% EQU 1 GOTO P1
IF %_chosenopt% EQU 2 GOTO P2
:END_P0
GOTO MENU


:P1
SET _tempvar=
ECHO: Available parent folders:
ECHO:
PUSHD "F:\"
SET /A "_num=0"
FOR /D %%G IN ("*") DO (
    SET /A "_num+=1"
    SET _folder=%%G
    SET _elem[!_num!]=!_folder!
    IF !_num! LEQ 9 ECHO:  !_num!. !_folder!
    IF !_num! GTR 9 ECHO: !_num!. !_folder!
)
POPD
ECHO:
ECHO:
SET /P _choice=Please choose a folder or press ENTER to quit: || GOTO END_P1

REM 1. %_choice% must be an integer number.
FOR /F "tokens=* delims=0123456789" %%A IN ("%_choice%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO P1

REM 2. %_choice% must be lower or equal than the number of available letters.
SET _ok=1
IF %_choice% LSS 1 SET _ok=0
IF %_choice% GTR %_num% SET _ok=0
IF %_ok% EQU 0 GOTO P1

REM 3. Grab folder once %_choice% is checked as valid.
FOR %%C IN (%_choice%) DO SET _key=!_elem[%%C]!

GOTO P3
:END_P1
GOTO MENU


:P2
SET _tempvar=
ECHO: Available artist folders:
ECHO:
PUSHD "F:\"
SET /A "_num=0"
FOR /D %%G IN ("*") DO (
    SET _curdir=
    POPD
    FOR %%H IN ("F:\%%G") DO SET _curdir=%%~fH
    PUSHD !_curdir!
    FOR /D %%I IN ("*") DO (
        SET /A "_num+=1"
        SET _folder=%%I
        SET _elem[!_num!]=!_folder!
        IF !_num! LEQ 9 ECHO:  !_num!. !_folder!
        IF !_num! GTR 9 ECHO: !_num!. !_folder!
    )
)
POPD
ECHO:
ECHO:
SET /P _choice=Please choose a folder or press ENTER to quit: || GOTO END_P2
python %_AUDIOCD%\Shared\check_choice.py %_choice% %_num%
IF ERRORLEVEL 1 GOTO P2
FOR %%C IN (%_choice%) DO SET _key=!_elem[%%C]!

GOTO P3
:END_P2
GOTO MENU


:P3

REM 1. Check modified files.
CALL:HEADER2
SET _answer=
CALL :QUESTION "YN" "20" "N" "Would you like to check if sync is required?" _answer

REM 2 Don't check modified files.
IF [%_answer%] EQU [N] GOTO P4

REM 3. Check modified files.
CLS
SET _src="F:\?*\%_key%\*\?*\*.flac"
SET _dst="\\DISKSTATION\music\"
SET _answer=
IF %_chosenopt% EQU 1 (
    SET _src="F:\%_key%\*\?*\*.flac"
    SET _dst="\\DISKSTATION\music\%_key%\"
)
XXCOPY %_src% %_dst% /EX:"%_exclusions%" /BI /FF /L /oA:%_XXCOPYLOG%
IF %ERRORLEVEL% EQU 0 SET /A _difference=1
ECHO:
ECHO:

REM 4. Sync is not required.
IF NOT DEFINED _difference (
    CALL :QUESTION "YN" "20" "N" "Sync is not required. Would you like to continue?" _answer
    IF [!_answer!] EQU [N] GOTO END_P3
)

REM 5. Sync is required.
IF DEFINED _difference (
    CALL :QUESTION "YN" "20" "N" "Sync is required. Would you like to continue?" _answer
    IF [!_answer!] EQU [N] GOTO END_P3
)

GOTO P4
:END_P3
GOTO MENU


REM 6. Continue flow by confirming or aborting.
:P4
CALL:HEADER2
ECHO:
ECHO:
SET _answer=
CALL :QUESTION "YN" "20" "N" "Please confirm your choice as XXCOPY application will copy local Hi-Res audio files to MyCloud." _answer
IF [%_answer%] EQU [N] GOTO END_P4
CLS
ECHO:
XXCOPY /EC %_src% %_dst% /EX:"%_exclusions%" /BI /FF /Y /KS /Fo:"%_COMPUTING%\Log\copied_/$YMMDD_K_HHNNSS$.lst" /FM:L /oA:%_XXCOPYLOG%
XXCOPY /CE "\\DISKSTATION\music\" "F:\" /X:*recycle\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%

ECHO:
ECHO:
PAUSE
:END_P4
GOTO MENU


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
SET _images=
SET _cmdfile=
DEL "cmdfile.txt" 2> NUL
CLS
ECHO Script is scanning MyCloud collection. Please be patient as it may take some time.
PUSHD "%_PYTHONPROJECT%\Images"
python Numbering.py "%_argument%" --debug


REM --------------
REM Rename images.
REM --------------
IF ERRORLEVEL 11 (
    PUSHD "%TEMP%"
    IF EXIST "cmdfile.txt" (
        FOR /F "usebackq delims=| tokens=1,2" %%A IN ("cmdfile.txt") DO (
            SET _images=%%~A
            SET _cmdfile=%%~B
        )
        ECHO:
        ECHO:
        ECHO !_images! image^(s^) need^(s^) to be renamed. Here is the renaming script:
        ECHO:
        ECHO:
        TYPE "!_cmdfile!"
        CALL :QUESTION "YN" "60" "N" "Please confirm you want to run this script." _answer
        IF [!_answer!] EQU [N] GOTO P01B
        CLS
        "!_cmdfile!"
        ECHO:
        ECHO:
        PAUSE
        GOTO P01B
    )
)


REM ------------
REM Move images.
REM ------------
IF ERRORLEVEL 10 (
    PUSHD "%TEMP%"
    IF EXIST "cmdfile.txt" (
        FOR /F "usebackq delims=| tokens=1,2" %%A IN ("cmdfile.txt") DO (
            SET _images=%%~A
            SET _cmdfile=%%~B
        )
        ECHO:
        ECHO:
        ECHO !_images! image^(s^) need^(s^) at first to be moved. Here is the moving script:
        ECHO:
        ECHO:
        TYPE "!_cmdfile!"
        CALL :QUESTION "YN" "60" "N" "Please confirm you want to run this script." _answer
        IF [!_answer!] EQU [N] GOTO P01B
        CLS
        "!_cmdfile!"
        ECHO:
        ECHO:
        PAUSE
        POPD
        POPD
        GOTO P01A
    )
)


REM ----------------
REM No images found.
REM ----------------
IF ERRORLEVEL 0 (
    ECHO:
    ECHO:
    ECHO Any images to rename haven't been found. Script will exit. && PAUSE && POPD && GOTO MENU
)


:P01B
POPD
POPD
GOTO MENU


:HEADER2
CLS
ECHO:
ECHO: ========================================
ECHO: =   MYCLOUD PARTIAL AUDIO FILES SYNC   =
ECHO: ========================================
EXIT /B 0


:QUESTION
SET %5=Y
ECHO:
ECHO:
CHOICE /C %~1 /T %~2 /N /D %~3 /M "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET %5=N
EXIT /B 0
