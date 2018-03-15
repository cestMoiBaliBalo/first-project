REM ===========
REM Exit codes.
REM ===========
REM 0: script worked well without any issues.
REM 1: no alterable tags menu can be displayed.
REM 2: no tags plain text file can be found into %TEMP% directory.
REM 3: exit without any alteration.
REM 4: An issue occurred into an external script.


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _databases[1]=%_PYTHONPROJECT%\Applications\Tests\database.db
SET _databases[2]=%_COMPUTING%\Resources\database.db
SET _command=
SET _count=
SET _first=1
SET _menu="artistsort;albumsort;artist;origyear;year;album;genre;label;upc;application;disc;tracks"
SET _tags=0


REM ==================
REM Initializations 3.
REM ==================
CALL "%_COMPUTING%\shared.cmd" GETOCCURENCES %_menu% ";"
SET _count=%ERRORLEVEL%
IF %_count% EQU 0 EXIT /B 1
FOR /F "delims=; tokens=1-%_count%" %%A IN (%_menu%) DO (
    SET _newvalue[%%A]=
    IF %_count% GEQ 2 SET _newvalue[%%B]=
    IF %_count% GEQ 3 SET _newvalue[%%C]=
    IF %_count% GEQ 4 SET _newvalue[%%D]=
    IF %_count% GEQ 5 SET _newvalue[%%E]=
    IF %_count% GEQ 6 SET _newvalue[%%F]=
    IF %_count% GEQ 7 SET _newvalue[%%G]=
    IF %_count% GEQ 8 SET _newvalue[%%H]=
    IF %_count% GEQ 9 SET _newvalue[%%I]=
    IF %_count% GEQ 10 SET _newvalue[%%J]=
    IF %_count% GEQ 11 SET _newvalue[%%K]=
    IF %_count% GEQ 12 SET _newvalue[%%L]=
)


REM    ================
REM A. Choose Database.
REM    ================
:DATABASE
CALL :HEADER
ECHO:
ECHO:
ECHO: 1. Test database
ECHO: 2. Production database (default^)
ECHO:
ECHO:
ECHO:
SET _tempvar=
SET /P _database=Please enter the required database or press ENTER to choose the default database: || SET _database=2
FOR /F "delims=|" %%A IN ("%_database%") DO SET _database=%%~A
FOR /F "tokens=* delims=12" %%A IN ("%_database%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO DATABASE
CALL SET _database=%%_databases[%_database%]%%


REM    =======================
REM B. Display available logs.
REM    =======================
PUSHD "%_PYTHONPROJECT%\AudioCD\Tools"
CALL rippinglogs.cmd "%_database%"
SET _rowid=%ERRORLEVEL%
POPD

REM B.2. Issue occurred into `rippinglogs.cmd`.
IF %_rowid% EQU -1 EXIT /B 4

REM B.3. Exit chosen into `rippinglogs.cmd`.
IF %_rowid% EQU 0 EXIT /B 3


REM    =============
REM C. Choose a log.
REM    =============
(
    PUSHD "%_PYTHONPROJECT%\AudioCD\Tools"
    python rippinglog.py "%_rowid%" --database "%_database%"
    IF ERRORLEVEL 1 (
        POPD
        ECHO:
        ECHO:
        ECHO: No data found for ROWID %_rowid%. Script will exit.
        ECHO:
        PAUSE & EXIT /B 2
    )
    POPD
)
SET _tagsfile=%TEMP%\rippinglog_%_rowid%.tmp
IF NOT EXIST "%_tagsfile%" EXIT /B 2


REM    ========================
REM D. Store chosen log detail.
REM    ========================
REM    Strip whitespaces at first.
FOR /F "usebackq delims=: tokens=1,*" %%I IN ("%_tagsfile%") DO (
    FOR /F "usebackq" %%A IN ('%%I') DO SET _key=%%A
    SET _value=%%~J
    SET _currvalue[!_key!]="!_value!"
)


REM    =======================
REM E. Alteration main script.
REM    =======================
:MENU
CALL :HEADER


REM    ------------------------------------
REM 1. Display chosen log detail.
REM    Keys, current values and new values.
REM    ------------------------------------
CALL :SUBHEADER


REM    ----------------------------
REM 2. Display alterable keys menu.
REM    ----------------------------
ECHO:
ECHO:
CALL "%_COMPUTING%\shared.cmd" GETOCCURENCES %_menu% ";"
SET _count=%ERRORLEVEL%
IF %_count% EQU 0 EXIT /B 1
FOR /F "delims=; tokens=1-%_count%" %%A IN (%_menu%) DO (
    (
        ECHO:  1. %%A
        SET _keys[1]=%%A
    )
    IF %_count% GEQ 2 (
        ECHO:  2. %%B
        SET _keys[2]=%%B
    )
    IF %_count% GEQ 3 (
        ECHO:  3. %%C
        SET _keys[3]=%%C
    )
    IF %_count% GEQ 4 (
        ECHO:  4. %%D
        SET _keys[4]=%%D
    )
    IF %_count% GEQ 5 (
        ECHO:  5. %%E
        SET _keys[5]=%%E
    )
    IF %_count% GEQ 6 (
        ECHO:  6. %%F
        SET _keys[6]=%%F
    )
    IF %_count% GEQ 7 (
        ECHO:  7. %%G
        SET _keys[7]=%%G
    )
    IF %_count% GEQ 8 (
        ECHO:  8. %%H
        SET _keys[8]=%%H
    )
    IF %_count% GEQ 9 (
        ECHO:  9. %%I
        SET _keys[9]=%%I
    )
    IF %_count% GEQ 10 (
        ECHO: 10. %%J
        SET _keys[10]=%%J
    )
    IF %_count% GEQ 11 (
        ECHO: 11. %%K
        SET _keys[11]=%%K
    )
    IF %_count% GEQ 12 (
        ECHO: 12. %%L
        SET _keys[12]=%%L
    )
)
ECHO:
ECHO:
ECHO:
IF %_first% EQU 0 (
    SET /P _key=Please choose the tag to alter or press ENTER to run alteration: || GOTO COMMAND
)
IF %_first% EQU 1 (
    SET /P _key=Please choose tag or press ENTER to quit: || EXIT /B 5
)
SET _tempvar=
FOR /F "tokens=* delims=0123456789" %%A IN ("%_key%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO MENU
SET _ok=1
IF %_key% LSS 1 SET _ok=0
IF %_key% GTR %_count% SET _ok=0
IF !_ok! EQU 0 GOTO MENU


REM    --------------------------------
REM 3. Convert key from number to name.
REM    --------------------------------
CALL SET _key=%%_keys[%_key%]%%


REM    --------------------------------------------------
REM 4. Display available genres if chosen key is `genre`.
REM    --------------------------------------------------
IF /I ["%_key%"] EQU ["genre"] (
:GENRE
    CALL :HEADER
    ECHO:
    ECHO:
    SET _num=0
    FOR /F "usebackq delims=|" %%G IN ("%_COMPUTING%\Resources\genres.txt") DO (
        SET /A "_num+=1"
        SET _genres[!_num!]=%%G
        SET _genre=%%G
        IF /I ["!_genre!"] EQU ["rock"] SET _genre=Rock (default^)
        IF !_num! LEQ 9 ECHO:  !_num!. !_genre!
        IF !_num! GTR 9 ECHO: !_num!. !_genre!
    )
    ECHO:
    ECHO:
    ECHO:
    SET /P _genre=Please choose new genre: || SET _genre=9
    SET _tempvar=
    FOR /F "tokens=* delims=0123456789" %%A IN ("!_genre!") DO SET _tempvar=%%A
    IF DEFINED _tempvar GOTO GENRE
    SET _ok=1
    IF !_genre! LSS 1 SET _ok=0
    IF !_genre! GTR !_num! SET _ok=0
    IF !_ok! EQU 0 GOTO GENRE
    FOR %%G IN (!_genre!) DO SET _genre=!_genres[%%G]!
    SET _value=!_genre!
)


REM    --------------------------------------------------
REM 5. Prompt for new value if chosen key is not `genre`.
REM    --------------------------------------------------
IF /I ["%_key%"] NEQ ["genre"] (
    SET /P _value=Please enter "%_key%" new value: || GOTO MENU
    FOR /F "delims=|" %%I IN ("!_value!") DO SET _value=%%~I
)


REM    --------------------------------
REM 6. Check if altered `upc` is valid.
REM    --------------------------------
IF /I ["%_key%"] EQU ["upc"] (
    PUSHD %_PYTHONPROJECT%
    python AudioCD/Tools/check_upc.py "%_value%"
    IF ERRORLEVEL 1 (
        POPD
        GOTO MENU
    )
    POPD
)


REM    --------------------------------------
REM 7. Check if altered `albumsort` is valid.
REM    --------------------------------------
IF /I ["%_key%"] EQU ["albumsort"] (
    PUSHD %_PYTHONPROJECT%
    python AudioCD/Tools/check_albumsort.py "%_value%"
    IF ERRORLEVEL 1 (
        POPD
        GOTO MENU
    )
    POPD
)


REM    -------------------------------------
REM 8. Check if altered `origyear` is valid.
REM    -------------------------------------
IF /I ["%_key%"] EQU ["origyear"] (
    PUSHD %_PYTHONPROJECT%
    python AudioCD/Tools/check_year.py "%_value%"
    IF ERRORLEVEL 1 (
        POPD
        GOTO MENU
    )
    POPD
)


REM    ---------------------------------
REM 9. Check if altered `year` is valid.
REM    ---------------------------------
IF /I ["%_key%"] EQU ["year"] (
    PUSHD %_PYTHONPROJECT%
    python AudioCD/Tools/check_year.py "%_value%"
    IF ERRORLEVEL 1 (
        POPD
        GOTO MENU
    )
    POPD
)


REM     --------------------------------------
REM 10. Compare current value and new value.
REM     Set _command if a difference is found.
REM     --------------------------------------
(
    CALL SET _current=%%_currvalue[%_key%]%%
    IF [!_current!] NEQ ["%_value%"] (
        SET /A "_tags+=1"
        SET _command=%_command%--%_key% "%_value%" 
        SET _newvalue[%_key%]=%_value%
    )
)


REM     ---------------------------
REM 11. Update alterable keys menu.
REM     ---------------------------
REM     Remove chosen key from menu.

REM     Remove quotes at first.
FOR /F "usebackq" %%M IN ('%_menu%') DO SET _menu=%%~M

REM     Look for the chosen tag into the menu.
CALL SET _result=%%_menu:;%_key%;=;%%

REM     Look for the chosen tag at the end of the menu.
IF /I ["%_result%"] EQU ["%_menu%"] CALL SET _result=%%_menu:;%_key%=%%

REM     Look for the chosen tag at the beginning of the menu.
REM     `year` must be processed in a different way because of `origyear`.
IF /I ["%_result%"] EQU ["%_menu%"] (
    IF /I ["%_key%"] NEQ ["year"] CALL SET _result=%%_menu:%_key%;=%%
    IF /I ["%_key%"] EQU ["year"] (
        IF /I ["%_menu:~0,5%"] EQU ["year;"] SET _result=%_menu:~5%
    )
)
IF /I ["%_result%"] EQU ["%_menu%"] GOTO COMMAND
IF /I ["%_result%"] NEQ ["%_menu%"] (
    SET _menu="%_result%"
    SET _first=0
    GOTO MENU
)


REM     -------------------------------------------
REM 12. Alter chosen key(s) by running `tables.py`.
REM     -------------------------------------------
:COMMAND
IF DEFINED _command (
    CALL :HEADER
    CALL :SUBHEADER
    ECHO:
    ECHO:
    ECHO:
    CHOICE /C YN /N /T 30 /D N /M "Would you like to alter the chosen log? Press [Y] for Yes or [N] for No."
    IF ERRORLEVEL 2 GOTO END
    SET _command=python tables.py rippinglog update %_rowid% %_command:~0,-1% --database "%_database%"
    (
        PUSHD "%_PYTHONPROJECT%\AudioCD"
        ECHO !_command!
        PAUSE
        POPD
    )
)


REM    ============
REM F. Exit script.
REM    ============
:END
DEL "%_tagsfile%" 2> nul
EXIT /B 0


:HEADER
CLS
ECHO:
ECHO: *******************************************
ECHO: *                                         *
ECHO: *   U P D A T E   R I P P I N G   L O G   *
ECHO: *                                         *
ECHO: *******************************************
EXIT /B 0


:SUBHEADER
ECHO:
ECHO:
SETLOCAL
FOR /F "usebackq delims=: tokens=1,*" %%I IN ("%_tagsfile%") DO (
    FOR /F "usebackq" %%A IN ('%%I') DO SET _key=%%A
    IF NOT DEFINED _newvalue[!_key!] ECHO: %%~I:%%J
    IF DEFINED _newvalue[!_key!] (
        CALL SET _x=%%_newvalue[!_key!]%%
        ECHO: %%~I:%%J!_x!
    )
)
(
    ENDLOCAL
    EXIT /B 0
)
