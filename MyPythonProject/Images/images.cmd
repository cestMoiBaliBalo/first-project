@REM __author__ = 'Xavier ROSSET'
@REM __maintainer__ = 'Xavier ROSSET'
@REM __email__ = 'xavier.python.computing@protonmail.com'
@REM __status__ = "Development"


@SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
@IF NOT DEFINED _caller (
    ECHO off
    CHCP 65001 > NUL
    CLS
)
@IF NOT DEFINED _action (
    ENDLOCAL
    EXIT /B 100
)
@IF NOT DEFINED _path (
    ENDLOCAL
    EXIT /B 100
)
@FOR /F "usebackq delims=" %%A IN ('%_path%') DO SET _path=%%~A
@IF NOT EXIST "%_path%" (
    ENDLOCAL
    EXIT /B 100
)


REM ==================
REM Initializations 1.
REM ==================
SET _caller=%~nx0
SET _me=%~n0
SET _myparent=%~dp0
FOR /F "usebackq delims=" %%A IN ('%_myparent%.') DO SET _myancestor=%%~dpA


REM ==================
REM Initializations 2.
REM ==================
SET _errorlevel=0
SET _images=images.txt


REM ==================
REM Initializations 3.
REM ==================
SET PATH=%_myancestor%VirtualEnv\venv38\Scripts;%PATH%
PUSHD %_myparent:~0,-1%


REM ============
REM Main script.
REM ============
:MAIN
CLS
IF [%_action%] EQU [DISPLAY] (
    CALL :PARSE_PATH
    CALL :GET_LENGTH
    IF !_length! EQU 0 GOTO THE_END
    IF !_length! GTR 4 SET _path=!_path:~0,4!
    GOTO DISPLAY
)
IF [%_action%] EQU [RENAME] (
    CALL :PARSE_PATH
    CALL :GET_LENGTH
    IF !_length! EQU 0 GOTO THE_END
    IF !_length! GTR 4 SET _path=!_path:~0,4!
    GOTO RENAME
)
IF [%_action%] EQU [INSERT] GOTO INSERT


REM        ---------------------------------
REM --> A. Display images original datetime.
REM        ---------------------------------
:DISPLAY
PUSHD %TEMP%
DEL %_images% 2> NUL
POPD
perl images.pl %_root%\%_path%
IF NOT ERRORLEVEL 1 (
    CLS
    python display.py %TEMP%\%_images%
    ECHO:
    ECHO:
    PAUSE
)
GOTO THE_END


REM        ---------------------------------------------
REM --> B. Rename images according to original datetime.
REM        ---------------------------------------------
:RENAME
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _year_2011=2011
SET _year_2012=2012
SET _year_2014=2014
SET _year_2003=2003*
SET _year_2004=2004*
SET _year_2005=2005*
SET _year_2006=2006*
SET _year_2007=2007*
SET _year_2008=2008*
SET _year_2009=2009*
SET _year_2010=2010*
SET _year_2013=2013*
SET _year_2015=2015*
SET _year_2016=2016*
SET _year_2017=2017*
SET _year_2018=2018*
SET _year_2019=2019*
SET _year_2020=2020*
SET _year_2021=2021*
SET _pattern_2004=%%Y
SET _pattern_2005=%%Y
SET _pattern_2006=%%Y
SET _pattern_2007=%%Y
SET _pattern_9999=%%Y%%m
SET _recursive_2011= -r
SET _recursive_2012= -r
SET _recursive_2014= -r

@REM -----
SET _pattern=!_pattern_%_path%!
IF NOT DEFINED _pattern_%_path% SET _pattern=%_pattern_9999%
SET _recursive=!_recursive_%_path%!

@REM -----
@CLS
@ECHO Append an "X" to the file name for preventing any duplicates which could lead to a failure.
@ECHO:
@PAUSE
perl "C:\ExifTool\exiftool"%_recursive% -ext jpg -FileOrder DateTimeOriginal -FileName=%%fX.%%e "%_root%\!_year_%_path%!"
@ECHO:
@ECHO:
@PAUSE

@REM -----
@CLS
@ECHO Rename files according to the original datetime.
@ECHO:
@PAUSE
perl "C:\ExifTool\exiftool"%_recursive% -ext jpg -FileOrder DateTimeOriginal "-FileName<DateTimeOriginal" -d %_pattern%_%%%%.5nC%%%%lE "%_root%\!_year_%_path%!"
ECHO:
ECHO:
PAUSE

@REM -----
ENDLOCAL
GOTO THE_END


REM        -------------------------------------------------
REM --> C. Insert new images according to original datetime.
REM        -------------------------------------------------
:INSERT
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
ECHO: perl "C:\ExifTool\exiftool" -ext jpg -FileOrder DateTimeOriginal "-Directory<DateTimeOriginal" -d H:\%%Y%%m "%_path%"
ECHO:
ECHO:
PAUSE
ENDLOCAL
GOTO THE_END


REM ============
REM Exit script.
REM ============
:THE_END
POPD
@(
    ENDLOCAL
    EXIT /B %_errorlevel%
)


REM ================
REM Local functions.
REM ================
:PARSE_PATH
SETLOCAL ENABLEEXTENSIONS
FOR /F "usebackq delims=" %%A IN ('%_path%') DO (
    SET _path=%%~nA
    SET _root=%%~dA
)
(
    ENDLOCAL
    SET _path=%_path%
    SET _root=%_root%
)
EXIT /B 0


:GET_LENGTH
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
SET _length=0
SET _offset=0
:LOOP
IF "!_path:~%_offset%,1!" NEQ "" (
    SET /A "_length+=1"
    SET /A "_offset+=1"
    GOTO LOOP
)
(
    ENDLOCAL
    SET _length=%_length%
)
EXIT /B 0
