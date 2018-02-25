@ECHO off

REM An ambitious DOS script performing computing tasks (such as backup files or syncing local/remote ressources).
REM A menu brought by a python script is displayed allowing to choose among some configured tasks.
REM DOS then performs both configuration of the execution environment and execution of the task itself.

REM
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
SET _cloud_avchd=\\DISKSTATION\backup\AVCHD Vidéos
SET _local_avchd=G:\Videos\AVCHD Videos
SET _lossless=G:\Music\Lossless
SET _lossy=G:\Music\Lossy
SET _exclusions=%_COMPUTING%\exclusions.txt
SET _exclusions1=%_COMPUTING%\exclusions1.txt
SET _sdcard=%_COMPUTING%\SDCard-content.txt
SET _sdcard_password=%_COMPUTING%\SDCard-password.txt
SET _menu_images=%_COMPUTING%\menu-images.txt
SET _copied=%TEMP%\copied.lst
SET _removed=%TEMP%\removed.lst
SET _tobearchived=%TEMP%\tobearchived.lst


REM ===============
REM Main algorithm.
REM ===============
CHCP 1252


REM -------------
REM Display menu.
REM -------------
:MENU
python %_PYTHONPROJECT%\Tasks\tasks.py


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM -------------------
REM Numbering pictures.
REM -------------------
IF ERRORLEVEL 36 (
    REM python %_PYTHONPROJECT%\Images\Numbering.py
    GOTO MENU
)


REM ------------------
REM Sort lists tester.
REM ------------------
IF ERRORLEVEL 33 (
    REM CLS
    REM PUSHD %_PYTHONPROJECT%
    REM python -m unittest -v Applications.Tests.module1.Test03
    REM POPD
    REM PAUSE
    GOTO MENU
)


REM -------------------------------
REM Default Audio CD ripper tester.
REM -------------------------------
IF ERRORLEVEL 32 (
    REM CLS
    REM python -m unittest -v Applications.Tests.module1
    REM PAUSE
    GOTO MENU
)


REM ---------------
REM Parsers tester.
REM ---------------
IF ERRORLEVEL 31 (
    REM CLS
    REM PUSHD %_PYTHONPROJECT%
    REM python -m unittest -v Applications.Tests.module2
    REM POPD
    REM PAUSE
    GOTO MENU
)


IF ERRORLEVEL 30 (
    CALL "C:\Users\Xavier\Downloads\DOS snippets\new5.cmd"
    GOTO MENU
)



REM ---------------------------
REM Regular expressions tester.
REM ---------------------------
IF ERRORLEVEL 29 (
    REM CLS
    REM python -m unittest -v Applications.Tests.module2
    REM PAUSE
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
    SET _tempvar=
    SET _answer=

    REM 1. Display available drives.
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
    SET /A "_num+=1"
    SET _elem[!_num!]=%TEMP%\
    IF !_num! LEQ 9 ECHO:  !_num!. System temporary folder
    IF !_num! GTR 9 ECHO: !_num!. System temporary folder
    ECHO:
    ECHO:
    SET /P _choice=Please choose a drive or press ENTER to quit: || GOTO FIN24

    REM 2. %_choice% must be an integer number.
    FOR /F "tokens=* delims=0123456789" %%A IN ("%_choice%") DO SET _tempvar=%%A
    IF DEFINED _tempvar GOTO MENU24

    REM 3. %_choice% must be lower or equal than the number of available drives.
    IF !_choice! GTR !_num! GOTO MENU24

    REM 4. Grab drive letter once %_choice% is checked as valid.
    FOR %%C IN (!_choice!) DO SET _drive=!_elem[%%C]!

    REM 5. Convert drive letter into a valid path.
    FOR %%D IN (!_drive!) DO SET "_drive=%%~fD"

    REM 6. Confirm or abort backup.
    CALL :HEADER4
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm as XXCOPY application will copy important personal files to your local SD Memory Card." _answer
    IF [!_answer!] EQU [N] GOTO FIN24

    REM 7. Backup every single files listed into "%_COMPUTING%\SDCard.txt".
    IF EXIST %_tobearchived% DEL %_tobearchived%
    CLS
    SET /A "_first=1"
    FOR /F "usebackq tokens=1" %%F IN ("%_sdcard%") DO (
        SET _switch=/CE
        IF !_first! EQU 1 SET _switch=/EC
        SET /A "_first=0"
        CALL SET _file=%%~F
        XXCOPY !_switch! "!_file!" "!_drive!" /KS /Y /BI /FF /Fo:%_copied% /FM:L /oA:%_XXCOPYLOG%
        IF !ERRORLEVEL! EQU 0 FOR /F "usebackq delims=|" %%I IN ("%_copied%") DO ECHO %%~nxI >> "%_tobearchived%"
    )
    ECHO:
    ECHO:

    REM 8. Backup important personal files.
    XXCOPY /EC "%_MYDOCUMENTS%\Administratif\*\?*\*.pdf" "!_drive!Administratif\" /CLONE /Z0 /Fo:%_copied% /FM:L /oA:%_XXCOPYLOG%
    IF !ERRORLEVEL! EQU 0 (
        FOR /F "usebackq delims=\ tokens=1-4,*" %%I IN ("%_copied%") DO (
            ECHO %%~M >> "%_tobearchived%"
        )
    )
    ECHO:
    ECHO:

    REM 9. Backup computing projects.
    XXCOPY /CE "%_COMPUTING%\" "!_drive!Computing\" /EX:"%_exclusions1%" /CLONE /Z0 /Fo:%_copied% /FM:L /oA:%_XXCOPYLOG%
    IF !ERRORLEVEL! EQU 0 (
        FOR /F "usebackq delims=\ tokens=1,*" %%I IN ("%_copied%") DO (
            ECHO %%~J >> "%_tobearchived%"
        )
    )
    ECHO:
    ECHO:

    REM 9. Create/Update 7-Zip archive.
    FOR /F "usebackq delims=|" %%I IN ("%_sdcard_password%") DO SET _password=%%~I
    IF EXIST %_tobearchived% (
        SET _exitcode=
        CALL :ARCHIVE "a" "7z" "!_drive!Documents" "!_password!" "WIN" "!_drive!" _exitcode "%_tobearchived%"
        IF !_exitcode! EQU 0 (
            IF ["!_drive!"] NEQ ["%TEMP%\"] XXCOPY "!_drive!" /RS /S /Y /X:*.7z /Fo:%_removed% /FM:L /oA:%_XXCOPYLOG%
        )
    )
    ECHO:
    ECHO:
    PAUSE

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


REM --------------------------------------------
REM Sync mobile device from lossless repository.
REM --------------------------------------------
IF ERRORLEVEL 19 (
    SET _difference=
    SET _drive=
    SET /A _islossy=0
    SET /A _islossless=1
    GOTO P5
)


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
    SET _ressource=
    SET _extension=
    CALL :LOG "%_copied%" _ressource _extension
    XXCOPY "F:\*\?*\*.flac" "\\DISKSTATION\music\" /EX:"%_exclusions%" /CLONE /PZ0 /Fo:"!_ressource!_/$YMMDD_K_HHNNSS$!_extension!" /FM:L /oA:%_XXCOPYLOG%
    ECHO:
    ECHO:
    PAUSE

:FIN17
    GOTO MENU

)


REM -----------------------------------------
REM Sync mobile device from lossy repository.
REM -----------------------------------------
IF ERRORLEVEL 16 (
    SET _difference=
    SET _drive=
    SET /A _islossy=1
    SET /A _islossless=0
    GOTO P5
)


REM --------------------------
REM Edit "rippinglog" content.
REM --------------------------
IF ERRORLEVEL 15 (
    CLS
    ECHO:
    ECHO:
    python %_PYTHONPROJECT%\AudioCD\Interface.py rippinglog select
    ECHO:
    PAUSE
    GOTO MENU
)


REM ---------------------------
REM MyCloud partial audio sync.
REM ---------------------------
IF ERRORLEVEL 14 GOTO P00


REM -------------------------------------
REM Digital audio files HTML simple view.
REM -------------------------------------
IF ERRORLEVEL 13 (
    REM python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
    REM IF NOT ERRORLEVEL 1 (
        REM IF EXIST "%_xmldigitalaudiobase%" (
            REM java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
            REM DEL "%_xmldigitalaudiobase%"
        REM )
    REM )
    GOTO MENU
)


REM ---------------------
REM Edit "tasks" content.
REM ---------------------
IF ERRORLEVEL 12 (
    CLS
    ECHO:
    ECHO:
    python %_PYTHONPROJECT%\AudioCD\Interface.py tasks select
    ECHO:
    PAUSE
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


REM =========================================================
REM Specific parts for syncing audio files to mobile devices.
REM =========================================================


:P5
SET _tempvar=

REM A. Display available drives.
CALL :HEADER3 %_islossless%
ECHO:
ECHO:
ECHO: Available drives:
ECHO:
SET /A "_num=0"
FOR /F "usebackq" %%G IN (`wmic logicaldisk get name ^| find ":"`) DO (
    SET /A "_num+=1"
    SET _letter=%%G
    SET _elem[!_num!]=!_letter!
    IF !_num! LEQ 9 ECHO:  !_num!. !_letter!
    IF !_num! GTR 9 ECHO: !_num!. !_letter!
)
SET /A "_num+=1"
SET _elem[!_num!]=%TEMP%\
IF !_num! LEQ 9 ECHO:  !_num!. System temporary folder
IF !_num! GTR 9 ECHO: !_num!. System temporary folder
ECHO:
ECHO:
ECHO:
SET /P _choice=Please choose a drive or press ENTER to quit: || GOTO END_P5

REM B. %_choice% must be an integer number.
FOR /F "tokens=* delims=0123456789" %%A IN ("%_choice%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO P5

REM C. %_choice% must be lower or equal than the number of available drives.
IF %_choice% GTR %_num% GOTO P5

REM D. Grab drive letter once %_choice% is checked as valid.
FOR %%C IN (%_choice%) DO SET _drive=!_elem[%%C]!

REM E. Convert drive letter into a valid path.
FOR %%D IN (%_drive%) DO SET "_drive=%%~fD"

REM F. Check modified files.
CALL :HEADER3 %_islossless%
SET _answer=
CALL :QUESTION "YN" "20" "Y" "Would you like to check if sync is required?" _answer

REM G. Don't check modified files.
IF [!_answer!] EQU [N] GOTO P6

REM H. Check modified files.
CLS
ECHO:
ECHO:

REM H.1. Lossless audio files.
IF %_islossless% EQU 1 (

    REM --> FLAC.
    ECHO:Check FLAC files...
    ECHO:
    ECHO:
    XXCOPY "%_lossless%\*\?*\*.flac" "%_drive%" /BI /FF /L /oA:%_XXCOPYLOG%
    IF !ERRORLEVEL! EQU 0 SET /A _difference=1

    REM --> DSD.
    ECHO:Check DSD files...
    ECHO:
    ECHO:
    XXCOPY "%_lossless%\*\?*\*.dsf" "%_drive%" /BI /FF /L /oA:%_XXCOPYLOG%
    IF !ERRORLEVEL! EQU 0 SET /A _difference=1

)

REM H.2. Lossy audio files.
IF %_islossy% EQU 1 (
    ECHO:Check MPEG Layer III files...
    ECHO:
    ECHO:
    XXCOPY "%_lossy%\*\?*\*.mp3" "%_drive%" /BI /FF /L /oA:%_XXCOPYLOG%
    IF !ERRORLEVEL! EQU 0 SET /A _difference=1
)

REM I. Sync is not required.
IF NOT DEFINED _difference (
    CALL :HEADER3 %_islossless%
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Sync is not required. Would you like to continue?" _answer
    IF [!_answer!] EQU [N] GOTO END_P5
)

REM J. Sync is required.
IF DEFINED _difference (
    CALL :HEADER3 %_islossless%
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Sync is required. Would you like to continue?" _answer
    IF [!_answer!] EQU [N] GOTO END_P5
)

GOTO P6
:END_P5
GOTO MENU


REM K. Continue flow by confirming or aborting.
:P6
SET _ressource=
SET _extension=
CALL :LOG "%_copied%" _ressource _extension

REM K.1. Lossless audio files.
IF %_islossless% EQU 1 (
    CALL :HEADER3 %_islossless%
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm your choice as XXCOPY application will copy local Hi-Res audio files to your mobile device." _answer
    IF [!_answer!] EQU [N] GOTO END_P6
    CLS
    ECHO:
    ECHO:

    REM K.1.a. Sync FLAC files.
    ECHO XXCOPY /EC "%_lossless%\*\?*\*.flac" "%_drive%" /KS /BI /FF /Y /Fo:"!_ressource!_/$YMMDD_K_HHNNSS$!_extension!" /FM:L /oA:%_XXCOPYLOG%

    REM K.1.b. Sync DSD files.
    ECHO XXCOPY /CE "%_lossless%\*\?*\*.dsf" "%_drive%" /KS /BI /FF /Y /Fo:"!_ressource!_/$YMMDD_K_HHNNSS$!_extension!" /FM:L /oA:%_XXCOPYLOG%

    REM K.1.c. Remove extra files not present into the destination directory. Preserve "DCIM" if present.
    ECHO XXCOPY /CE "%_drive%" "%_lossless%\" /RS /S /BB /PD0 /Y /X:DCIM\ /oA:%_XXCOPYLOG%
)

REM K.2. Lossy audio files.
IF %_islossy% EQU 1 (
    CALL :HEADER3 %_islossless%
    SET _answer=
    CALL :QUESTION "YN" "20" "N" "Please confirm your choice as XXCOPY application will copy local Low-Res audio files to your mobile device." _answer
    IF [!_answer!] EQU [N] GOTO END_P6
    CLS
    ECHO:
    ECHO:
    ECHO XXCOPY /EC "%_lossy%\*\?*\*.mp3" "%_drive%" /KS /BI /FF /Y /Fo:"!_ressource!_/$YMMDD_K_HHNNSS$!_extension!" /FM:L /oA:%_XXCOPYLOG%
    ECHO XXCOPY /CE "%_drive%" "%_lossy%\" /RS /S /BB /PD0 /Y /X:DCIM\ /oA:%_XXCOPYLOG%
)

ECHO:
ECHO:
PAUSE
:END_P6
GOTO MENU


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
ECHO:  1. By parent folder.
ECHO:  2. By artist folder.
ECHO:
ECHO:
SET /P _choice=Please choose an option or press ENTER to quit: || GOTO END_P00

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
IF %_choice% GTR %_num% GOTO P1

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

REM 1. %_choice% must be an integer number.
FOR /F "tokens=* delims=0123456789" %%A IN ("%_choice%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO P2

REM 2. %_choice% must be lower or equal than the number of available letters.
IF %_choice% GTR %_num% GOTO P2

REM 3. Grab folder once %_choice% is checked as valid.
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
SET _ressource=
SET _extension=
CALL :LOG "%_copied%" _ressource _extension
XXCOPY /EC %_src% %_dst% /EX:"%_exclusions%" /BI /FF /Y /KS /Fo:"!_ressource!_/$YMMDD_K_HHNNSS$!_extension!" /FM:L /oA:%_XXCOPYLOG%
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
CHOICE /C YN /T 20 /N /d N /m "Would you like to set copyright? Press [Y] for Yes or [N] for No."
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
CALL:HEADER1 %_choice%
ECHO:
ECHO:
SET /P _index=Please enter starting index : || GOTO COMMAND
FOR /F "usebackq delims=|" %%I IN ('%_index%') DO SET _index=%%~I
FOR /F "usebackq delims=0123456789 tokens=*" %%I IN ('%_index%') DO SET _tempvar=%%I
IF DEFINED _tempvar GOTO INDEX
IF %_index% EQU 0 GOTO INDEX
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
        CHOICE /m "The following command will be run: !_command!. Do you agree?"
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


:HEADER3
CLS
ECHO:
IF [%1] EQU [1] (
    ECHO: ===================================================
    ECHO: =   SYNC MOBILE DEVICE FROM LOSSLESS REPOSITORY   =
    ECHO: ===================================================
)
IF [%1] EQU [0] (
    ECHO: ===================================================
    ECHO: =    SYNC MOBILE DEVICE FROM LOSSY REPOSITORY     =
    ECHO: ===================================================
)
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
CHOICE /C %~1 /T %~2 /N /d %~3 /m "%~4 Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET %5=N
EXIT /B 0


:ARCHIVE
REM     %1 : archive command. Add (default) or Update.
REM     %2 : archive type. 7z (default) or zip.
REM     %3 : archive name.
REM     %4 : password. Facultative.
REM     %5 : files list encoding. UTF-8 (default) or WIN.
REM     %6 : current directory. Facultative.
REM     %7 : 7-Zip exit code.
REM     %8 : files list. Mandatory. From 1 to N.
SETLOCAL ENABLEDELAYEDEXPANSION
SET _currdir=
SET /A "_run=0"

REM 1. Initialize command.
IF ["%~1"] EQU [""] SET _command=a -y
IF ["%~1"] NEQ [""] SET _command=%~1 -y

REM 2. Append archive type if defined.
IF ["%~2"] EQU [""] SET _command=%_command% -t7z
IF ["%~2"] NEQ [""] SET _command=%_command% -t%~2

REM 3. Append password if defined.
IF ["%~4"] NEQ [""] SET _command=%_command% -p"%~4"

REM 4. Append files list encoding if defined.
IF ["%~5"] EQU [""] SET _command=%_command% -scsUTF-8
IF ["%~5"] NEQ [""] SET _command=%_command% -scs%~5

REM 5. Append archive name.
FOR %%I IN ("%~3") DO (
    IF ["%~2"] EQU [""] SET _command=%_command% "%%~nI.7z"
    IF ["%~2"] NEQ [""] SET _command=%_command% "%%~nI.%~2"
)

REM 6. Get working directory.
IF ["%~6"] EQU [""] FOR /F "usebackq" %%I IN (`CD`) DO SET _currdir=%%I
IF ["%~6"] NEQ [""] SET _currdir=%~6
IF NOT EXIST "%_currdir%" (
    ENDLOCAL
    SET %7=100
    GOTO FIN_ARCHIVE
)

REM 6. Append files list(s).
:LISTS
SET _list=%~8
IF NOT DEFINED _list GOTO FIN_LISTS
IF DEFINED _list (
    SET _command=%_command% @"%_list%"
    SET /A "_run=1"
)
SHIFT /8
GOTO LISTS

REM 7. Run 7-Zip command.
:FIN_LISTS
(
    IF %_run% EQU 1 (
        SET _question=The following command will be run: %_command%. Would you like to continue?
        SET _answer=
        REM CALL :QUESTION "YN" "20" "Y" "!_question!" _answer
        REM IF ["!_answer!"] EQU ["Y"] (
            PUSHD "%_currdir%"
            "C:\Program Files\7-Zip\7z.exe" %_command%
            ENDLOCAL
            SET %7=!ERRORLEVEL!
            POPD
            GOTO FIN_ARCHIVE
        REM )
    )
    ENDLOCAL
    SET %7=100
    GOTO FIN_ARCHIVE
)

:FIN_ARCHIVE
EXIT /B 0


:LOG
FOR /F "usebackq delims=|" %%I IN ('%~1') DO (
    SET %2=%%~dpnI
    SET %3=%%~xI
)
EXIT /B 0
