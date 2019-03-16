@ECHO off
IF [%~1]==[A] (
    SET "_OLD_PATH=%PATH%"
    SET "PATH=%_PYTHONPROJECT%\VirtualEnv\%~2\Scripts;%PATH%"
)
IF [%~1]==[D] (
    IF DEFINED _OLD_PATH (
        SET "PATH=%_OLD_PATH%"
        SET _OLD_PATH=
    )
)
EXIT /B 0
