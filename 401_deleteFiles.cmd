@ECHO off

REM
SETLOCAL ENABLEEXTENSIONS

REM Initializations.
SET _me=%~n0
SET _myparent=%~dp0

REM Main algorithm.
:START
IF "%~1"=="" EXIT /B 0

:MAIN
REM sdelete -p 3 -s -q "%~1"
ECHO "%~1">%TEMP%\toto.txt
SHIFT
GOTO START
