REM ===========
REM Exit codes.
REM ===========
REM 0: script worked well without any issues.
REM 1: no tags plain text file can be found into %TEMP% directory.
REM 2: exit without any alteration.
REM 3: An issue occurred into an external script.


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
SET _index=0
FOR /L %%I IN (1, 1, 50) DO SET _rows[%%I]=


REM    ===============
REM A. Choose Database.
REM    ===============
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
SET /P _database=Please enter the required database: || SET _database=2
FOR /F "delims=|" %%A IN ("%_database%") DO SET _database=%%~A
FOR /F "tokens=* delims=12" %%A IN ("%_database%") DO SET _tempvar=%%A
IF DEFINED _tempvar GOTO DATABASE
CALL SET _database=%%_databases[%_database%]%%


REM    =======================
REM B. Display available logs.
REM    =======================
PUSHD "%_PYTHONPROJECT%\AudioCD\Tools"
CALL rippinglogs.cmd %_database%
SET _rowid=%ERRORLEVEL%
POPD

REM B.2. Issue occurred into `rippinglogs.cmd`.
IF %_rowid% EQU -1 EXIT /B 3

REM B.3. Exit chosen into `rippinglogs.cmd`.
IF %_rowid% EQU 0 EXIT /B 2


REM    =============
REM C. Choose a log.
REM    =============
(
    PUSHD "%_PYTHONPROJECT%\AudioCD\Tools"
    python rippinglog.py "%_rowid%" --database %_database%
    IF ERRORLEVEL 1 (
        POPD
        ECHO:
        ECHO:
        ECHO: No data found for ROWID %_rowid%. Script will exit.
        ECHO:
        PAUSE & EXIT /B 1
    )
    POPD
)
SET _tagsfile=%TEMP%\rippinglog_%_rowid%.tmp
IF NOT EXIST "%_tagsfile%" EXIT /B 1


REM    ===========================
REM D. Store the chosen log ROWID.
REM    ===========================
SET /A "_index+=1"
SET _rows[%_index%]=%_rowid%


REM    =========================================
REM E. Delete chosen log by running `tables.py`.
REM    =========================================
CALL :HEADER
CALL :SUBHEADER
ECHO:
ECHO:
ECHO:
CHOICE /C YN /N /T 30 /D N /M "Would you like to delete the chosen log? Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 GOTO END
SET _command=python tables.py rippinglog delete %_rowid% --database %_database%
(
    PUSHD "%_PYTHONPROJECT%\AudioCD"
    ECHO %_command%
    PAUSE
    POPD
)


REM    ===============
REM F. Exit algorithm.
REM    ===============
:END
DEL "%_tagsfile%" 2> nul
EXIT /B 0


:HEADER
CLS
ECHO:
ECHO: *******************************************
ECHO: *                                         *
ECHO: *   D E L E T E   R I P P I N G   L O G   *
ECHO: *                                         *
ECHO: *******************************************
EXIT /B 0


:SUBHEADER
ECHO:
ECHO:
FOR /F "usebackq delims=|" %%I IN ("%_tagsfile%") DO ECHO: %%~I
EXIT /B 0
