REM __author__ = 'Xavier ROSSET'
REM __maintainer__ = 'Xavier ROSSET'
REM __email__ = 'xavier.python.computing@protonmail.com'
REM __status__ = "Development"


REM ================
REM Initializations.
REM ================
SET _AUDIOCD=%_PYTHONPROJECT%\AudioCD
SET _EXIFTOOL=G:\Computing\Resources\exiftool.exe
SET _command=
SET _end=0
SET _images=\\diskstation\backup\images\collection


REM ============
REM Main script.
REM ============
FOR /F "usebackq" %%I IN (`DATE /T`) DO SET _date=%%I
FOR /F "usebackq" %%I IN (`TIME /T`) DO SET _time=%%I


REM    --------------------------
REM A. Display available folders.
REM    --------------------------
:FOLDERS

REM --- Remove me please!
REM SET _images=%TEMP%
REM SET _folder=201803
REM SET _count=149
REM GOTO INDEX
REM --- Remove me please!

SET _num=0
CLS
ECHO:
ECHO:
FOR /F "usebackq" %%I IN (`DIR /B /O:N %_images%`) DO (
    SET /A "_num+=1"
    IF !_num! LEQ 9 ECHO:   !_num!. %%~nI
    IF !_num! GTR 9 IF !_num! LEQ 99 ECHO:  !_num!. %%~nI
    IF !_num! GTR 99 ECHO: !_num!. %%~nI
    SET _folders[!_num!]=%%~nI
)


REM    -----------
REM B. Set folder.
REM    -----------
:FOLDER
(
    ECHO:
    ECHO:
    SET /P _choice=Please choose folder or press ENTER to quit: || (SET _errorlevel=100& GOTO END)
    python %_AUDIOCD%\Tools\check_choice.py !_choice! %_num%
    IF ERRORLEVEL 1 GOTO FOLDERS
    CALL SET _folder=%%_folders[!_choice!]%%
)
(
    ECHO:
    ECHO:
    SET _count=0
    FOR %%I IN ("%_images%\%_folder%\*.jpg") DO SET /A "_count+=1"
    ECHO:
    ECHO:
    ECHO: !_count! JPG images found in %_images%\%_folder%.
    ECHO:
    ECHO:
    PAUSE
)


REM    ---------------------------------
REM C. Set index to start renaming from.
REM    ---------------------------------
:INDEX
SET _errorlevel=0
CLS
ECHO:
ECHO:
SET /P _index=Please choose index to start renaming from: || SET _index=1
SET /A "_end=_index+_count-1"


REM    -----------------
REM D. Confirm renaming.
REM    -----------------
CLS
ECHO:
ECHO:
CHOICE /C YN /T 30 /N /d N /M "Would you like to rename found files from number %_index% to number %_end%? Press [Y] for Yes or [N] for No."
IF ERRORLEVEL 2 SET _errorlevel=100

REM Rename images temporary from 1 to %_index% to prevent any duplicate issue.
IF %_errorlevel% EQU 0 (
    SET _command="%_EXIFTOOL%" -FileName=%%1.5C.%%e -ext jpg -fileOrder DateTimeOriginal "%_images%\%_folder%"
    ECHO %_date% - %_time% - !_command! >> %_COMPUTING%\Log\ripper.txt
    ECHO:
    ECHO:
    !_command!
    SET _errorlevel=!ERRORLEVEL!
)

REM Rename images from %_index% to %_end%.
IF %_errorlevel% EQU 0 (
    SET _command="%_EXIFTOOL%" "-FileName<DateTimeOriginal" -d %%Y_%%%%%_index%.5C.%%%%e -ext jpg -fileOrder DateTimeOriginal "%_images%\%_folder%"
    ECHO %_date% - %_time% - !_command! >> %_COMPUTING%\Log\ripper.txt
    ECHO:
    ECHO:
    !_command!
    SET _errorlevel=!ERRORLEVEL!
)


REM    ------------
REM E. Exit script.
REM    ------------
:END
ECHO:
ECHO:
ECHO Exit code is: %_errorlevel%
ECHO:
ECHO:
PAUSE
EXIT /B %_errorlevel%
