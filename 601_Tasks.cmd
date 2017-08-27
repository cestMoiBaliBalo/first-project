@ECHO off

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
SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase


REM ===============
REM Main algorithm.
REM ===============
COLOR 3F


REM -------------
REM Display menu.
REM -------------
:MENU
python %_PYTHONPROJECT%\Tasks\Tasks.py


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM -------------------
REM Clone music to NAS.
REM -------------------
IF ERRORLEVEL 38 (
    REM "G:\Computing\start.cmd" 15
    GOTO MENU
)


REM --------------------
REM Clone images to NAS.
REM --------------------
IF ERRORLEVEL 37 (
    REM "G:\Computing\start.cmd" 14
    GOTO MENU
)


REM -------------------
REM Numbering pictures.
REM -------------------
IF ERRORLEVEL 36 (
    python %_PYTHONPROJECT%\Images\Numbering.py
    GOTO MENU
)


REM ----------------------------------
REM Delete "rippinglog" table records.
REM ----------------------------------
IF ERRORLEVEL 35 (
    python %_PYTHONPROJECT%\AudioCD\Delete.py
    GOTO MENU
)


REM --------------------
REM Edit folder content.
REM --------------------
IF ERRORLEVEL 34 (
    python %_PYTHONPROJECT%\Files\FolderContent.py
    GOTO MENU
)


REM ------------------
REM Sort lists tester.
REM ------------------
IF ERRORLEVEL 33 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.Test03
    POPD
    PAUSE
    GOTO MENU
)


REM -------------------------------
REM Default Audio CD ripper tester.
REM -------------------------------
IF ERRORLEVEL 32 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.Test01DefaultCDTrack Applications.Tests.module1.Test02DefaultCDTrack Applications.Tests.module1.Test03DefaultCDTrack Applications.Tests.module1.Test04DefaultCDTrack Applications.Tests.module1.Test05DefaultCDTrack Applications.Tests.module1.Test06DefaultCDTrack Applications.Tests.module1.Test07DefaultCDTrack Applications.Tests.module1.Test08DefaultCDTrack
    POPD
    PAUSE
    GOTO MENU
)


REM ---------------
REM Parsers tester.
REM ---------------
IF ERRORLEVEL 31 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module2
    POPD
    PAUSE
    GOTO MENU
)


REM ----------------------------------
REM Update "rippinglog" table records.
REM ----------------------------------
IF ERRORLEVEL 30 (
    python %_PYTHONPROJECT%\AudioCD\Update.py
    GOTO MENU
)


REM ---------------------------
REM Regular expressions tester.
REM ---------------------------
IF ERRORLEVEL 29 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.TestRegex
    POPD
    PAUSE
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


REM -------------------
REM Convert Unix epoch.
REM -------------------
IF ERRORLEVEL 24 (
    REM python Applications`convertUnixEpoch`L.py
    REM IF ERRORLEVEL 11 GOTO MENU
    GOTO MENU
)


REM -------------------------
REM Get Unix epoch from date.
REM -------------------------
IF ERRORLEVEL 23 (
    REM python Applications`getUnixEpoch`L.py
    GOTO MENU
)


REM ----------------------
REM Timestamp audio files.
REM ----------------------
IF ERRORLEVEL 22 (
    REM python AudioFiles`Taggingtime`L.py
    GOTO MENU
)


REM ---------------------------
REM Display geometric sequence.
REM ---------------------------
IF ERRORLEVEL 18 (
    REM python Math`Sequences`L.py G
    GOTO MENU
)


REM ----------------------------
REM Display arithmetic sequence.
REM ---------------------------
IF ERRORLEVEL 17 (
    REM python Math`Sequences`L.py A
    GOTO MENU
)


REM --------------------------
REM Edit "rippinglog" content.
REM --------------------------
IF ERRORLEVEL 15 (
    python %_PYTHONPROJECT%\AudioCD\RippedCD`View1.py
    python %_PYTHONPROJECT%\AudioCD\RippedCD`View2.py
    CLS
    python %_PYTHONPROJECT%\AudioCD\RippedCD`View3.py
    PAUSE
    GOTO MENU
)


REM -------------------------------------
REM Digital audio files HTML simple view.
REM -------------------------------------
IF ERRORLEVEL 13 (
    python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View.py
    IF NOT ERRORLEVEL 1 (
        IF EXIST "%_xmldigitalaudiobase%" (
            java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
            DEL "%_xmldigitalaudiobase%"
        )
    )
    GOTO MENU
)


REM ------------------------
REM Edit "rundates" content.
REM ------------------------
IF ERRORLEVEL 12 (
    CLS
    python %_PYTHONPROJECT%\Tasks\Dates.py "rundates"
    PAUSE
    GOTO MENU
)


REM -----------------------
REM Edit "backups" content.
REM -----------------------
IF ERRORLEVEL 11 (
    CLS
    python %_PYTHONPROJECT%\Tasks\Dates.py "backups"
    PAUSE
    GOTO MENU
)


REM ----------------------
REM Backup python scripts.
REM ----------------------
IF ERRORLEVEL 10 (
    REM CALL "G:\Computing\start.cmd" 6
    GOTO MENU
)


REM --------------
REM Backup videos.
REM --------------
IF ERRORLEVEL 9 (
    CALL "G:\Computing\start.cmd" 12
    GOTO MENU
)


REM -----------------
REM Backup documents.
REM -----------------
IF ERRORLEVEL 8 (

    REM Run Backup.
    REM python G:\Computing\MyPythonProject\Areca\Areca.py -c documents 1282856126

    REM Update last run date.
    REM python -m Applications.Database.LastRunDates.dbLastRunDates update 123456797

    GOTO MENU
)


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
