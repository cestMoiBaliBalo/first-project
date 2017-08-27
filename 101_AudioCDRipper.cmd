@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _json=%TEMP%\arguments.json
SET _jsonrippedcd=%TEMP%\rippinglog.json
SET _htmlrippinglog=%_COMPUTING%\rippingLog\rippinglog.html
SET _jsonrippedtracks=%TEMP%\digitalaudiodatabase.json
SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase


REM ===============
REM Main algorithm.
REM ===============


:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
IF "%~1" EQU "6" GOTO STEP6
SHIFT
GOTO MAIN


REM        ------------
REM  1 --> Ripping log.
REM        ------------
:STEP1
IF EXIST "%_jsonrippedcd%" (
    python %_PYTHONPROJECT%\AudioCD\RippedCD.py "%_jsonrippedcd%"
    DEL "%_jsonrippedcd%"
)
SHIFT
GOTO MAIN


REM        -----------------------
REM  2 --> Digital audio database.
REM        -----------------------
:STEP2
IF EXIST "%_jsonrippedtracks%" (
    python %_PYTHONPROJECT%\AudioCD\RippedTracks.py "%_jsonrippedtracks%"
    DEL "%_jsonrippedtracks%"
)
SHIFT
GOTO MAIN


REM        -------------------------
REM  3 --> Update Ripping log views.
REM        -------------------------
:STEP3
python %_PYTHONPROJECT%\AudioCD\RippedCD`View1.py
python %_PYTHONPROJECT%\AudioCD\RippedCD`View2.py
SHIFT
GOTO MAIN


REM        ------------------------------------
REM  4 --> Update Digital Audio database views.
REM        ------------------------------------
:STEP4
REM PUSHD "%_PYTHONPROJECT%"
REM python AudioCD\DigitalAudioFiles`View1.py
REM python AudioCD\DigitalAudioFiles`View2.py
REM python Database\DigitalAudioFiles`View3.py
REM POPD
REM IF EXIST "%_xmldigitalaudiobase%" (
REM     java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
REM     DEL "%_xmldigitalaudiobase%"
REM )
SHIFT
GOTO MAIN


REM        -----------------
REM  5 --> Copy audio files.
REM        -----------------
:STEP5
REM START "" /B /D %_COMPUTING% 102_AudioCDRipper.cmd "%_json%" 30
SHIFT
GOTO MAIN


REM        -------------------
REM  6 --> Change "album" tag.
REM        -------------------
:STEP6
REM START "" /B /D %_COMPUTING% 104_AudioCDRipper.cmd 90
SHIFT
GOTO MAIN
