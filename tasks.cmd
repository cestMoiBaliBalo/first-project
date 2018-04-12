@ECHO off


REM An ambitious DOS script performing computing tasks (such as backup files or syncing local/remote resources).
REM A menu brought by a python script is displayed allowing to choose among some configured tasks.
REM DOS then performs both configuration of the execution environment and execution of the task itself.


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
::SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
::SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase
SET _AUDIOCD=%_PYTHONPROJECT%\AudioCD
SET _RESOURCES=%_COMPUTING%\Resources
SET _cloud_avchd=\\DISKSTATION\backup\AVCHD Vidéos
SET _copied=%TEMP%\copied.lst
SET _cp=1252
SET _echo=0
SET _local_avchd=G:\Videos\AVCHD Videos
SET _exclusions=%_RESOURCES%\exclusions.txt
SET _exclusions1=%_RESOURCES%\exclusions1.txt
SET _sdcard=%_RESOURCES%\SDCard-content.txt
SET _sdcard_password=%_RESOURCES%\SDCard-password.txt
SET _tobearchived=%TEMP%\tobearchived.lst
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


REM -------------------
REM Numbering pictures.
REM -------------------
IF ERRORLEVEL 36 (
    GOTO MENU
)


REM -----------------------------------
REM Delete log from `rippinglog` table.
REM -----------------------------------
IF ERRORLEVEL 35 (
    PUSHD "%_PYTHONPROJECT%\Tasks\05"
    python delete.py
    POPD
    GOTO MENU
)


REM ------------------
REM Sort lists tester.
REM ------------------
IF ERRORLEVEL 33 (
    GOTO MENU
)


REM -------------------------------
REM Default Audio CD ripper tester.
REM -------------------------------
IF ERRORLEVEL 32 (
    GOTO MENU
)


REM ---------------
REM Parsers tester.
REM ---------------
IF ERRORLEVEL 31 (
    GOTO MENU
)


REM -----------------------------------
REM Update log from `rippinglog` table.
REM -----------------------------------
IF ERRORLEVEL 30 (
    PUSHD "%_PYTHONPROJECT%\Tasks\05"
    python update.py
    POPD
    GOTO MENU
)


REM ---------------------------
REM Regular expressions tester.
REM ---------------------------
IF ERRORLEVEL 29 (
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 200* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 28 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1222562470
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2009 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 27 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1068554868
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 201* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 26 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1306312508
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2016 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 25 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1066663185
    GOTO MENU
)


REM ----------------------------------------
REM Backup personal files to SD Memory Card.
REM ----------------------------------------
IF ERRORLEVEL 24 (

:MENU24
    SET _answer=
    SET _first=1
    SET _temp=%TEMP%\PersonalDocuments
    DEL %_copied% %_tobearchived% 2> NUL

    REM 1. Set backup destination.
    REM    %TEMP% is available for test purposes.
    CALL :HEADER4
    ECHO:
    ECHO:
    ECHO: Available drives:
    ECHO:
    SET /A "_num=0"
    FOR /F "usebackq" %%A IN (`wmic logicaldisk get name ^| find ":"`) DO (
        SET /A "_num+=1"
        SET _letter=%%A
        SET _elem[!_num!]=!_letter!
        IF !_num! LEQ 9 ECHO:  !_num!. !_letter!
        IF !_num! GTR 9 ECHO: !_num!. !_letter!
    )
    ECHO:
    ECHO:
    SET /P _choice=Please choose a drive or press ENTER to quit: || GOTO FIN24
    python %_AUDIOCD%\Tools\check_choice.py !_choice! !_num!
    IF ERRORLEVEL 1 GOTO MENU24

    REM 2. Grab backup destination once %_choice% is checked as valid.
    FOR %%C IN (!_choice!) DO SET _drive=!_elem[%%C]!

    REM 3. Convert backup destination into a valid path.
    FOR %%D IN (!_drive!) DO SET "_drive=%%~fD"

    REM 4. Set backup type.
:ARCHIVE_TYPE
    CALL :HEADER4
    ECHO:
    ECHO:
    ECHO: Backup type:
    ECHO:
    ECHO: 1. Differential backup (default^)
    ECHO: 2. Full backup
    ECHO:
    ECHO:
    SET /P _backuptype=Please choose backup type: || SET _backuptype=1
    python %_AUDIOCD%\Tools\check_choice.py !_backuptype! "2"
    IF ERRORLEVEL 1 GOTO ARCHIVE_TYPE

    REM 5. Confirm or abort backup.
    CALL :HEADER4
    ECHO:
    ECHO:
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy important personal files to your local SD Memory Card." _answer
    IF [!_answer!] EQU [N] GOTO FIN24
    CLS

    REM 6. Extract content of 7-Zip archive.
    IF !_backuptype! EQU 1 (
        IF EXIST "!_drive!Documents.7z" (
            XXCOPY "!_drive!Documents.7z" "!_temp!\" /Y /oA:%_XXCOPYLOG%
            IF ERRORLEVEL 1 GOTO FIN24
            IF ERRORLEVEL 0 (
                FOR /F "usebackq delims=|" %%I IN ("%_sdcard_password%") DO (
                    SET _password=%%~I
                    PUSHD !_temp!
                    "C:\Program Files\7-Zip\7z.exe" x -y -p"!_password!" "Documents.7z"
                    POPD
                )
            )
        )
    )

    REM 7. Backup every single files listed into "%_COMPUTING%\SDCard.txt".
    SET _first=1
    FOR /F "usebackq tokens=1,2,* delims=|" %%F IN ("%_sdcard%") DO (
        SET _tokens=%%H
        (
            SET _switch=/CE
            IF !_first! EQU 1 SET _switch=/EC
        )
        SET _first=0
        CALL SET _file=%%~F
        IF [%%~G] EQU [] (
            XXCOPY !_switch! "!_file!" "!_temp!\" /KS /Y /BI /FF /Fo:%_copied% /FM:L /oA:%_XXCOPYLOG%
            IF !ERRORLEVEL! EQU 0 CALL :TOKENIZE "!_tokens!"
        )
        IF [%%~G] NEQ [] (
            XXCOPY !_switch! "!_file!" "!_temp!\%%~G\" /KS /Y /BI /FF /Fo:%_copied% /FM:L /oA:%_XXCOPYLOG%
            IF !ERRORLEVEL! EQU 0 CALL :TOKENIZE "!_tokens!"
        )
        ECHO:
        ECHO:
    )

    REM 8. Create/Update 7-Zip archive.
    IF EXIST %_tobearchived% (
        FOR /F "usebackq delims=|" %%I IN ("%_sdcard_password%") DO (
            SET _password=%%~I
            CALL "%_COMPUTING%\shared.cmd" "ARCHIVE" "a" "7z" "Documents" "!_password!" "WIN" "!_temp!" "%_tobearchived%"
            IF !ERRORLEVEL! EQU 0 (
                XXCOPY /EC "!_temp!\Documents.7z" "!_drive!" /Y /oA:%_XXCOPYLOG%
                XXCOPY /CE !_temp! /RMDIR /RSY /oA:%_XXCOPYLOG%
            )
            GOTO FIN24
        )
    )
    IF NOT EXIST %_tobearchived% IF EXIST "!_temp!" XXCOPY "!_temp!" /RMDIR /RSY /oA:%_XXCOPYLOG%

:FIN24
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
    CLS

    REM -->  1. Clone "\\DISKSTATION\Images\Collection" to local drive H. Don't delete extra files and directories!
    XXCOPY /EC "\\DISKSTATION\backup\Images\Collection\*\?*\*.jpg" "H:\" /CLONE /Z0 /oA:%_XXCOPYLOG%

    REM -->  2. Reverse both source and destination. Then remove brand new files but preserve some folders content.
    REM         - "RECYCLER".
    REM         - "$RECYCLE.BIN".
    REM         - "SYSTEM VOLUME INFORMATION".
    REM         - "IPHONE".
    REM         - "RECOVER".
    XXCOPY /CE "H:\" "\\DISKSTATION\backup\Images\Collection\" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%

    REM -->  3. Then pause.
    ECHO:
    ECHO:
    PAUSE

:FIN23
    GOTO MENU

)


REM -----------------
REM Not used anymore.
REM -----------------
IF ERRORLEVEL 20 GOTO MENU


REM -----------------
REM Not used anymore.
REM -----------------
IF ERRORLEVEL 19 GOTO MENU


REM ------------------------
REM MyCloud full video sync.
REM ------------------------
REM Delete extra files.
IF ERRORLEVEL 18 (
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
    CLS

:MENU17
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy local FLAC audio files to MyCloud." _answer
    IF [!_answer!] EQU [N] GOTO FIN18
    CLS
    XXCOPY "F:\*\?*\*.flac" "\\DISKSTATION\music\" /EX:"%_exclusions%" /CLONE /PZ0 /Fo:"%_COMPUTING%\Log\copied_/$YMMDD_K_HHNNSS$_lst" /FM:L /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:FIN17
    GOTO MENU

)


REM -----------------------------------------
REM Sync mobile device from audio repository.
REM -----------------------------------------
IF ERRORLEVEL 16 (
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD "%_PYTHONPROJECT%\Tasks\02"
    python main.py
    IF !ERRORLEVEL! EQU 0 (
        PUSHD "%TEMP%"
        IF EXIST "%_xxcopy%" (
            CALL "%_xxcopy%"
            ECHO.
            ECHO.
            PAUSE
        )
        POPD
    )
    POPD
    GOTO MENU
)


REM --------------------------
REM Edit "rippinglog" content.
REM --------------------------
IF ERRORLEVEL 15 (
    CLS
    ECHO:
    ECHO:
    python %_PYTHONPROJECT%\Tasks\tables.py rippinglog select
    ECHO:
    PAUSE
    GOTO MENU
)


REM ---------------------------
REM MyCloud partial audio sync.
REM ---------------------------
IF ERRORLEVEL 14 GOTO P00


REM ------------------------
REM Sync audio repositories.
REM ------------------------
IF ERRORLEVEL 13 (
    DEL "%TEMP%\%_xxcopy%" 2> NUL
    PUSHD "%_PYTHONPROJECT%\Tasks\01"
    python main.py
    IF !ERRORLEVEL! EQU 0 (
        PUSHD "%TEMP%"
        IF EXIST "%_xxcopy%" (
            CALL "%_xxcopy%"
            ECHO.
            ECHO.
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


REM ---------------------
REM Edit "tasks" content.
REM ---------------------
IF ERRORLEVEL 12 (
    CLS
    ECHO:
    ECHO:
    python %_PYTHONPROJECT%\Tasks\tables.py tasks select
    ECHO:
    PAUSE
    GOTO MENU
)


REM ---------------------
REM Images renaming task.
REM ---------------------
IF ERRORLEVEL 11 (
    CALL "G:\Computing\images.cmd"
    GOTO MENU
)


REM -----------------------
REM Display folder content.
REM -----------------------
IF ERRORLEVEL 10 (
    PUSHD "%_PYTHONPROJECT%\Tasks\03"
    python main.py
    POPD
    GOTO MENU

)


REM -----------------------
REM Update python packages.
REM -----------------------
IF ERRORLEVEL 9 (
    CLS
    pip install -U --upgrade-strategy="only-if-needed" -r "%_COMPUTING%\pip-commands.txt"
    ECHO:
    ECHO:
    PAUSE
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2017 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 8 (
    REM python %_PYTHONPROJECT%\Areca\Areca.py -c music 1066663185
    GOTO MENU
)


REM -----------------
REM Backup documents.
REM -----------------
REM IF ERRORLEVEL 8 (

    REM Run Backup.
    REM python %_COMPUTING%\MyPythonProject\Areca\Areca.py -c documents 1282856126

    REM Update last run date.
    REM python -m Applications.Database.LastRunDates.dbLastRunDates update 123456797

    GOTO MENU
REM )


REM --------------------------------------
REM Pearl Jam 2011 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 7 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1484552884
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2010 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 6 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 445045058
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2006 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 5 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1404261019
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2003 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 4 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1557918403
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2000 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 3 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1460302155
    GOTO MENU
)


REM --------------------------
REM Pearl Jam bootlegs backup.
REM --------------------------
IF ERRORLEVEL 2 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1460302155 1557918403 1404261019 445045058 1484552884
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 854796030 1674209532 1196865155 1535780732 204959095
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
python %_AUDIOCD%\Tools\check_choice.py %_choice% %_num%
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
XXCOPY /EC %_src% %_dst% /EX:"%_exclusions%" /BI /FF /Y /KS /Fo:"%_COMPUTING%\Log\copied_/$YMMDD_K_HHNNSS$_lst" /FM:L /oA:%_XXCOPYLOG%
XXCOPY /CE "\\DISKSTATION\music\" "F:\" /X:*recycle\ /RS /S /BB /PD0 /Y /oA:%_XXCOPYLOG%

ECHO:
ECHO:
PAUSE
:END_P4
GOTO MENU


REM =====================================
REM Specific parts for images processing.
REM =====================================


:IMAGES
SET _run=
SET _dirs=
SET _keywords=
SET _command=


REM    ----------
REM A. Main menu.
REM    ----------
:DISPLAY
SET _menu_images=Read;Rename;Write
CLS
ECHO:
ECHO: =========================
ECHO: =   IMAGES PROCESSING   =
ECHO: =========================
ECHO:
SET /A "_num=0"
FOR /F "usebackq delims=|" %%A IN ("%_menu_images%") DO (
    SET /A "_num+=1"
    ECHO:  !_num!. %%A.
)
ECHO:
ECHO:
SET /P _choice=Please enter choice or press ENTER to quit. || GOTO END_DISPLAY
IF %_choice% GTR %_num% GOTO DISPLAY
IF %_choice% EQU 1 GOTO FILES
IF %_choice% EQU 2 GOTO FILES
IF %_choice% EQU 3 GOTO END_DISPLAY
:END_DISPLAY
GOTO END_IMAGES


REM    --------------------------------
REM B. Set single files or directories.
REM    --------------------------------
:FILES
SET /A "_num=0"

:STEP1
CALL:HEADER1 %_choice%
ECHO:
ECHO:
SET /P _dir=Please enter files. Directories are accepted too. Press ENTER to quit. || GOTO STEP2
FOR /F "usebackq delims=|" %%D IN ('%_dir%') DO SET _dir=%%~D
ECHO:
ECHO:
IF NOT EXIST "%_dir%" (
    ECHO "%_dir%" doesn't exist!
    ECHO:
    ECHO:
    PAUSE
    GOTO STEP1
)
SET /A "_num+=1"
SET _dirs[%_num%]="%_dir%"
GOTO STEP1

:STEP2
FOR /L %%I IN (1, 1, %_num%) DO (
    SET _command=!_command!!_dirs[%%I]! 
)
IF NOT DEFINED _command GOTO END_FILES
IF %_choice% EQU 1 GOTO INDEX
IF %_choice% EQU 2 GOTO KEYWORDS

:END_FILES
GOTO END_IMAGES


REM    ---------------------------
REM C. Set keyword(s) to write to.
REM    ---------------------------
REM    Facultative.
:KEYWORDS
SET /A "_num=0"

:STEP3
CALL:HEADER1 %_choice%
ECHO:
ECHO:
SET /P _keyword=Enter keyword or press ENTER to quit: || GOTO STEP4
SET /A "_num+=1"
FOR /F "usebackq delims=|" %%K IN ('%_keyword%') DO SET _keywords[%_num%]="%%~K"
GOTO STEP3

:STEP4
FOR /L %%I IN (1, 1, %_num%) DO (
    SET _command=!_command!--keyword !_keywords[%%I]! 
    SET /A "_run=1"
)
GOTO COPYRIGHT

:END_KEYWORDS
GOTO END_IMAGES


REM    --------------------------
REM D. Set Copyright to write to.
REM    --------------------------
REM    Facultative.
:COPYRIGHT
CALL:HEADER1 %_choice%
ECHO:
ECHO:
CHOICE /C YN /T 20 /N /d N /M "Would you like to set copyright? Press [Y] for Yes or [N] for No."
IF %ERRORLEVEL% EQU 1 (
    SET _command=!_command!--copyright
    SET /A "_run=1"
)
GOTO LOCATION
:END_COPYRIGHT
GOTO END_IMAGES


REM    -------------------------
REM E. Set Location to write to.
REM    -------------------------
:LOCATION
CALL:HEADER1 %_choice%
ECHO:
ECHO:
SET /P _location=Please enter location || GOTO COMMAND
FOR /F "usebackq delims=|" %%L IN ('%_location%') DO SET _location="%%~L"
SET _command=!_command!--location %_location%
SET /A "_run=1"
GOTO COMMAND
:END_LOCATION
GOTO END_IMAGES


REM    -------------------------------
REM F. Starting index for rename mode.
REM    -------------------------------
:INDEX
SET _tempvar=
SET _ok=1
CALL:HEADER1 %_choice%
ECHO:
ECHO:
SET /P _index=Please enter starting index : || GOTO COMMAND
FOR /F "usebackq delims=|" %%I IN ('%_index%') DO SET _index=%%~I
FOR /F "usebackq delims=0123456789 tokens=*" %%I IN ('%_index%') DO SET _tempvar=%%I
IF DEFINED _tempvar GOTO INDEX
IF %_index% EQU 0 SET _ok=0
IF %_ok% EQU 0 GOTO INDEX
SET _command=!_command!--index "%_index%"
SET /A "_run=1"
GOTO COMMAND
:END_INDEX
GOTO END_IMAGES


REM    ------------
REM G. Run command.
REM    ------------
:COMMAND
IF DEFINED _command (
    IF DEFINED _run (
        CALL:HEADER1 %_choice%
        ECHO:
        ECHO:
        CALL:FUNCTION1 %_choice% _command
        SET _command=python script.py !_command!
        CHOICE /M "The following command will be run: !_command!. Do you agree?"
        IF ERRORLEVEL 2 GOTO END_COMMAND
        CLS
        PUSHD %_PYTHONPROJECT%
        !_command!
        POPD
        ECHO:
        ECHO:
        PAUSE
    )
)
:END_COMMAND
GOTO END_IMAGES


REM    ------------------
REM H. Back to main menu.
REM    ------------------
:END_IMAGES
GOTO MENU


REM =================
REM Common functions.
REM =================
:HEADER1
CLS
ECHO:
IF [%1] EQU [1] (
    ECHO: =========================
    ECHO: =      RENAME MODE      =
    ECHO: =========================
)
IF [%1] EQU [2] (
    ECHO: =========================
    ECHO: =      WRITE MODE       =
    ECHO: =========================
)
IF [%1] EQU [3] (
    ECHO: =========================
    ECHO: =       READ MODE       =
    ECHO: =========================
)
EXIT /B 0


:HEADER2
CLS
ECHO:
ECHO: ========================================
ECHO: =   MYCLOUD PARTIAL AUDIO FILES SYNC   =
ECHO: ========================================
EXIT /B 0


:HEADER4
CLS
ECHO:
ECHO: ===============================================
ECHO: =   BACKUP PERSONAL FILES TO SD MEMORY CARD   =
ECHO: ===============================================
EXIT /B 0


:FUNCTION1
SETLOCAL ENABLEDELAYEDEXPANSION
(
    ENDLOCAL
    IF [%1] EQU [1] (
        SET %2=rename !%~2!
    )
    IF [%1] EQU [2] (
        SET %2=write !%~2!
    )
    IF [%1] EQU [3] (
        SET %2=read !%~2!
    )
)
EXIT /B 0


:QUESTION
SET %5=Y
ECHO:
ECHO:
CHOICE /C %~1 /T %~2 /N /d %~3 /M "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET %5=N
EXIT /B 0


:TOKENIZE
SETLOCAL
SET _options=usebackq
IF ["%~1"] NEQ [""] SET _options="%_options% tokens=%~1 delims=\"
IF ["%~1"] EQU [""] SET _options="%_options% delims="
FOR /F %_options% %%I IN ("%_copied%") DO (
    IF ["%~1"] NEQ [""] SET _file=%%J
    IF ["%~1"] EQU [""] SET _file=%%~nxI
    ECHO !_file!>> "%_tobearchived%"
)
ENDLOCAL
EXIT /B 0
