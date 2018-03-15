@ECHO off
SETLOCAL ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
:MAIN
FOR /L %%I IN (1, 1, 10) DO SET _genres[%%I]=
SET _value=0


REM    ================
REM A. Choose Database.
REM    ================
:DATABASE
CLS
ECHO:
ECHO:
ECHO: 1. Test Database.
ECHO: 2. Production Database (default^).
ECHO:
ECHO:
SET /P _database=Please choose impacted base or press ENTER to choose default base: || SET _database=2


REM    ===============
REM B. Set Artistsort.
REM    ===============
:ARTISTSORT
CLS
ECHO:
ECHO:
SET /P _artistsort=Enter ArtistSort or press ENTER to quit: || GOTO FIN


REM    ==============
REM C. Set Albumsort.
REM    ==============
:ALBUMSORT
CLS
ECHO:
ECHO:
SET /P _albumsort=Enter AlbumSort or press ENTER to quit: || GOTO FIN
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tools
REM CALL check_albumsort.py %_albumsort%
REM IF ERRORLEVEL 1 (POPD & GOTO ALBUMSORT)
REM POPD


REM    ===========
REM D. Set Artist.
REM    ===========
:ARTIST
CLS
ECHO:
ECHO:
SET /P _artist=Enter Artist or press ENTER to quit: || GOTO FIN


REM    =============
REM E. Set Origyear.
REM    =============
:ORIGYEAR
CLS
ECHO:
ECHO:
SET /P _origyear=Enter OrigYear or press ENTER to quit: || GOTO FIN
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tools
REM CALL check_year.py %_origyear%
REM IF ERRORLEVEL 1 (POPD & GOTO ORIGYEAR)
REM POPD


REM    =========
REM F. Set Year.
REM    =========
:YEAR
CLS
ECHO:
ECHO:
SET /P _year=Enter Year or press ENTER to quit: || GOTO FIN
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tools
REM CALL check_year.py %_year%
REM IF ERRORLEVEL 1 (POPD & GOTO YEAR)
REM POPD


REM    ==========
REM G. Set Album.
REM    ==========
:ALBUM
CLS
ECHO:
ECHO:
SET /P _album=Enter Album or press ENTER to quit: || GOTO FIN


REM    ==========
REM H. Set Genre.
REM    ==========
:GENRE
CLS
ECHO:
ECHO:
SET _num=0
FOR /F "usebackq delims=|" %%G IN ("H:\My Documents\Personnel\genres.txt") DO (
    SET /A "_num+=1"
    SET _genres[!_num!]=%%G
    ECHO: !_num!. %%G
)
ECHO:
ECHO:
SET /P _genre=Enter Genre or press ENTER to choose default: || SET _genre=9
CALL SET _genre=%%_genres[%_genre%]%%


REM    ==========
REM I. Set Label.
REM    ==========
:LABEL
CLS
ECHO:
ECHO:
SET /P _label=Enter Label or press ENTER to quit: || GOTO FIN


REM    ========
REM J. Set UPC.
REM    ========
:UPC
CLS
ECHO:
ECHO:
SET /P _upc=Enter UPC or press ENTER to quit: || GOTO FIN
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tools
REM CALL check_upc.py %_upc%
REM IF ERRORLEVEL 1 (POPD & GOTO UPC)
REM POPD


REM    ================
REM K. Set Ripped date.
REM    ================
:RIPPED
CLS
ECHO:
ECHO:
SET /P _ripped=Enter Ripped UTC timestamp or press ENTER to quit: || GOTO FIN
REM PUSHD %_PYTHONPROJECT%\AudioCD\Tools
REM CALL check_timestamp.py %_ripped%
REM IF ERRORLEVEL 1 (POPD & GOTO RIPPED)
REM POPD


FOR /F "delims=|" %%A IN ("%_artistsort%") DO SET _artistsort="%%~A"
FOR /F "delims=|" %%A IN ("%_albumsort%") DO SET _albumsort="%%~A"
FOR /F "delims=|" %%A IN ("%_artist%") DO SET _artist="%%~A"
FOR /F "delims=|" %%A IN ("%_origyear%") DO SET _origyear="%%~A"
FOR /F "delims=|" %%A IN ("%_year%") DO SET _year="%%~A"
FOR /F "delims=|" %%A IN ("%_album%") DO SET _album="%%~A"
FOR /F "delims=|" %%A IN ("%_genre%") DO SET _genre="%%~A"
FOR /F "delims=|" %%A IN ("%_label%") DO SET _label="%%~A"
FOR /F "delims=|" %%A IN ("%_upc%") DO SET _upc="%%~A"
FOR /F "delims=|" %%A IN ("%_ripped%") DO SET _ripped="%%~A"
SET _command=python tables.py rippinglog insertfromargs %_artistsort% %_albumsort% %_artist% %_origyear% %_year% %_album% %_genre% %_label% %_upc% %_ripped%
IF %_database% EQU 1 SET _command=%_command% --test
CLS
ECHO:
ECHO:
REM PUSHD
ECHO: %_command%
REM SET /A "_value+=%ERRORLEVEL%"
REM POPD
REM CLS
REM ECHO:
REM ECHO:
REM CHOICE /C YN /T 10 /D N /N /M "Would you like to insert a record again?"
REM IF ERRORLEVEL 2 GOTO FIN
REM IF ERRORLEVEL 1 GOTO MAIN

:FIN
CLS
EXIT /B %_value%

