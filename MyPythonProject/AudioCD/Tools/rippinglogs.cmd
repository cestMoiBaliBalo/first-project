REM %1: Database.
REM %2: Page number.
REM %3: Logs per page.


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _database=%_COMPUTING%\Resources\database.db
SET _itemsperpage=40
SET _logs=C:\Users\Xavier\AppData\Local\Temp\rippinglogs.tmp
SET _pagenumber=1


REM ==============
REM Get arguments.
REM ==============
IF ["%~1"] NEQ [""] SET _database=%~1
IF ["%~2"] NEQ [""] SET _pagenumber=%~2
IF ["%~3"] NEQ [""] SET _itemsperpage=%~3


REM ================================
REM Get logs from `rippinglog` table.
REM ================================
:MAIN
PUSHD "%_PYTHONPROJECT%\AudioCD\Tools"
python rippinglogs.py --pagenumber %_pagenumber% --itemsperpage %_itemsperpage% --database %_database%
SET _totalpages=%ERRORLEVEL%
POPD
IF NOT EXIST "%_logs%" (
    SET _rowid=-1
    GOTO END
)


REM =============
REM Display logs.
REM =============
SET _nextlabel=
SET _num=0
SET _previouslabel=
FOR /L %%I IN (1, 1, %_itemsperpage%) DO SET _rows[%%I]=

REM Next pages.
SET /A "_nextpages=%_pagenumber%+1"
IF %_nextpages% GTR %_totalpages% SET _nextlabel=
IF %_nextpages% EQU %_totalpages% SET _nextlabel=Next page: %_totalpages%
IF %_nextpages% LSS %_totalpages% SET _nextlabel=Next pages: %_nextpages%-%_totalpages%

REM Previous pages.
SET /A "_previouspages=%_pagenumber%-1"
IF %_previouspages% LSS 1 SET _previouslabel=
IF %_previouspages% EQU 1 SET _previouslabel=Previous page: %_previouspages%
IF %_previouspages% GTR 1 SET _previouslabel=Previous pages: 1-%_previouspages%

REM Display logs.
CLS
ECHO:
ECHO:
IF DEFINED _previouslabel ECHO: %_previouslabel%
ECHO:
ECHO:
FOR /F "usebackq delims=| tokens=1-2" %%I IN ("%_logs%") DO (
    SET /A "_num+=1"
    SET _rows[!_num!]=%%J
    IF !_num! LEQ 9 ECHO:   !_num!. %%I
    IF !_num! GTR 9 IF !_num! LEQ 99 ECHO:  !_num!. %%I
    IF !_num! GTR 99 ECHO: !_num!. %%I
)
ECHO:
ECHO:
IF DEFINED _nextlabel ECHO: %_nextlabel%

REM Display availabel actions.
IF %_pagenumber% EQU 1 (
    SET _message=[N] for next page, [L] to pick up a log, [R] to request a page number or [Q] to quit.
    SET _choice=NLRQ
    SET _case=1
)
IF %_pagenumber% EQU %_totalpages% (
    SET _message=[P] for previous page, [L] to pick up a log, [R] to request a page number or [Q] to quit.
    SET _choice=PLRQ
    SET _case=2
)
IF %_totalpages% EQU 1 (
    SET _message=[L] to pick up a log or [Q] to quit.
    SET _choice=LQ
    SET _case=3
)
IF %_pagenumber% GTR 1 (
    IF %_totalpages% GTR 1 (
        IF %_pagenumber% LSS %_totalpages% (
            SET _message=[N] for next page, [P] for previous page, [L] to pick up a log, [R] to request a page number or [Q] to quit.
            SET _choice=NPLRQ
            SET _case=4
        )
    )
)
ECHO:
ECHO:
SET _currentpage=%_pagenumber%
CHOICE /C %_choice% /N /T 30 /D Q /M "%_message%"
SET _errorlevel=%ERRORLEVEL%
IF %_case% EQU 1 (
    IF %_errorlevel% EQU 4 (SET _rowid=0& GOTO END)
    IF %_errorlevel% EQU 3 GOTO PAGENUMBER
    IF %_errorlevel% EQU 2 GOTO ROWID
    IF %_errorlevel% EQU 1 (
        SET /A "_pagenumber+=1"
        GOTO MAIN
    )
)
IF %_case% EQU 2 (
    IF %_errorlevel% EQU 4 (SET _rowid=0& GOTO END)
    IF %_errorlevel% EQU 3 GOTO PAGENUMBER
    IF %_errorlevel% EQU 2 GOTO ROWID
    IF %_errorlevel% EQU 1 (
        SET /A "_pagenumber-=1"
        GOTO MAIN
    )
)
IF %_case% EQU 3 (
    IF %_errorlevel% EQU 2 (SET _rowid=0& GOTO END)
    IF %_errorlevel% EQU 1 GOTO ROWID
)
IF %_case% EQU 4 (
    IF %_errorlevel% EQU 5 (SET _rowid=0& GOTO END)
    IF %_errorlevel% EQU 4 GOTO PAGENUMBER
    IF %_errorlevel% EQU 3 GOTO ROWID
    IF %_errorlevel% EQU 2 (
        SET /A "_pagenumber-=1"
        GOTO MAIN
    )
    IF %_errorlevel% EQU 1 (
        SET /A "_pagenumber+=1"
        GOTO MAIN
    )
)


:PAGENUMBER
ECHO:
ECHO:
SET _tempvar=
SET /P _pagenumber=Enter the requested page number: 
FOR /F "delims=|" %%A IN ("%_pagenumber%") DO SET _pagenumber=%%~A
FOR /F "tokens=* delims=0123456789" %%A IN ("%_pagenumber%") DO SET _tempvar=%%A
IF DEFINED _tempvar (
    SET _pagenumber=%_currentpage%
    GOTO MAIN
)
SET _ok=1
IF %_pagenumber% LSS 1 SET _ok=0
IF %_pagenumber% GTR %_totalpages% SET _ok=0
IF %_pagenumber% EQU %_currentpage% SET _ok=0
IF %_ok% EQU 0 SET _pagenumber=%_currentpage%
GOTO MAIN


:ROWID
ECHO:
ECHO:
SET /P _rowid=Enter log number or press ENTER to quit: || (SET _rowid=0& GOTO END)
CALL SET _rowid=%%_rows[%_rowid%]%%


:END
EXIT /B %_rowid%
