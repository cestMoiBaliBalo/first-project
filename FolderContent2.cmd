@ECHO off
CLS
SETLOCAL
SET _count=counts.txt
SET _drive=%~1
SET _drive=%_drive:\=/%
PUSHD %TEMP%
DEL %_count% 2> NUL
PUSHD G:\Computing\MyPythonProject\Tasks
python toto.py "%_drive%" && python toto1.py
IF ERRORLEVEL 1 (
    POPD
    IF EXIST %_count% TYPE %_count%
)
POPD
SET _count=
SET _drive=
ENDLOCAL
ECHO:
ECHO:
PAUSE
EXIT /B 0
