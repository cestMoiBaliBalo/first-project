REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Production"
SETLOCAL ENABLEDELAYEDEXPANSION


REM ================
REM Initializations.
REM ================
SET _me=%~n0
SET _myparent=%~dp0


REM ============
REM Main script.
REM ============
IF ["%~1"] EQU [""] GOTO END

REM A. Get string length.
IF ["%~1"] EQU ["GETLENGTH"] (
    SET _result=
    CALL :GETLENGTH _result "%~2"
    (
        ENDLOCAL
        EXIT /B !_result!
    )
)

REM B. Get number of occurences from a separated string.
IF ["%~1"] EQU ["GETOCCURENCES"] (
    SET _result=
    CALL :GET_OCCURENCES _result "%~2" "%~3"
    (
        ENDLOCAL
        EXIT /B !_result!
    )
)

REM C. Update 7-Zip archive content.
IF ["%~1"] EQU ["ARCHIVE"] (

    SET _files=
    SET _run=0
    SET _command="%~2"
    SET _type="%~3"
    SET _name="%~4"
    SET _password="%~5"
    SET _encoding="%~6"
    SET _currdir="%~7"

:FILES1
    SET _list="%~8"
    IF [!_list!] EQU [""] GOTO END_FILES1
    SET _files=!_files!!_list! 
    SET _run=1
    SHIFT /8
    GOTO FILES1

:END_FILES1
    IF !_run! EQU 1 (
        CALL :ARCHIVE !_command! !_type! !_name! !_password! !_encoding! !_currdir! _exit !_files:~0,-1!
        EXIT /B !_exit!
    )
    (
        ENDLOCAL
        EXIT /B 100
    )

)

:END
(
    ENDLOCAL
    EXIT /B 0
)


REM    ==================
REM A. Get string length.
REM    ==================
:GETLENGTH
REM     %1: returned string length.
REM     %2: input string.
SETLOCAL ENABLEDELAYEDEXPANSION
SET _string=%~2
SET len=0
for %%P in (4096 2048 1024 512 256 128 64 32 16 8 4 2 1) DO (
    IF ["!_string:~%%P,1!"] NEQ [""] (
        SET /A "len+=%%P"
        SET _string=!_string:~%%P!
    )
)
SET /A "len+=1"
( 
    ENDLOCAL
    SET %~1=%len%
)
EXIT /B 0


REM    =============================
REM B. Update 7-Zip archive content.
REM    =============================
:ARCHIVE
REM     %1: archive command. Add (default) or Update.
REM     %2: archive type. 7z (default) or zip.
REM     %3: archive name.
REM     %4: password. Facultative.
REM     %5: files list encoding. UTF-8 (default) or WIN.
REM     %6: current directory. Facultative.
REM     %7: 7-Zip exit code.
REM     %8: files list. Mandatory. From 1 to N.
SETLOCAL ENABLEDELAYEDEXPANSION
SET _currdir=
SET _run=0

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
    GOTO END_ARCHIVE
)

REM 6. Append files list(s).
:FILES2
SET _list=%8
IF NOT DEFINED _list GOTO END_FILES2
IF DEFINED _list (
    SET _command=%_command% @%_list%
    SET _run=1
)
SHIFT /8
GOTO FILES2
:END_FILES2

REM 7. Run 7-Zip command.
(
    IF %_run% EQU 1 (
        PUSHD "%_currdir%"
        "C:\Program Files\7-Zip\7z.exe" %_command%
        ENDLOCAL
        SET %7=!ERRORLEVEL!
        POPD
        GOTO END_ARCHIVE
    )
    ENDLOCAL
    SET %7=100
    GOTO END_ARCHIVE
)

:END_ARCHIVE
EXIT /B 0


REM    =================================================
REM C. Get number of occurences from a separated string.
REM    =================================================
:GET_OCCURENCES
REM     %1: returned number of occurences.
REM     %2: input string.
REM     %3: separator.
SETLOCAL
SET _count=0
SET _string=%~2
SET _separator=%~3
:LOOP1
CALL SET _result=%%_string:*%_separator%=%%
IF ["%_result%"] NEQ ["%_string%"] (
    SET /A "_count+=1"
    SET _string=%_result%
    GOTO LOOP1
)
SET /A "_count+=1"
(
    ENDLOCAL
    SET %~1=%_count%
)
EXIT /B 0
