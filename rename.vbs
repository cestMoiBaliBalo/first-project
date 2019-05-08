Option Explicit
Dim argument, computing, fil, folder, fso, oshell, subfolder, stream, txtfile, txtobj


' --------- '
' Constants '
' --------- '
Const ForWriting = 2
Const TristateUseDefault = -2


' --------- '
' Arguments '
' --------- '
Set argument = Wscript.Arguments


' --------------- '
' Initializations '
' --------------- '
Set fso = CreateObject("Scripting.FileSystemObject")
Set oshell = CreateObject( "WScript.Shell" )


' ------------------------------- '
' Set output Windows command file '
' ------------------------------- '
txtfile = oshell.ExpandEnvironmentStrings("%_COMPUTING%") & "\rename.cmd"
fso.CreateTextFile txtfile
Set txtobj = fso.GetFile(txtfile)
Set stream = txtobj.OpenAsTextStream(ForWriting, TristateUseDefault)


' ------------- '
' Script header '
' ------------- '
stream.WriteLine "@ECHO off"
stream.WriteLine "SETLOCAL"
stream.WriteLine "SET _count=0"
stream.WriteLine "SET _cp=1252"
stream.WriteLine "FOR /F ""usebackq delims=: tokens=2"" %%I IN (`CHCP`) DO FOR /F ""usebackq"" %%J IN (" & Chr(39) & "%%I" & Chr(39) & ") DO IF %%J NEQ %_cp% CHCP %_cp% > NUL"
stream.WriteLine "CLS"


' ------------- '
' Script detail '
' ------------- '
On Error Resume Next
Set folder = fso.GetFolder(argument(0))
For Each subfolder in folder.SubFolders
    stream.WriteBlankLines(1)
    stream.WriteLine "PUSHD """ & subfolder.Path & """"
    For Each fil in subfolder.Files
        stream.WriteLine "RENAME """ & fil.Name & """ """ & fil.Name & """ && SET /A ""_count+=1"""
    Next
    stream.WriteLine "POPD"
Next


' ------------- '
' Script footer '
' ------------- '
stream.WriteBlankLines(1)
stream.WriteLine "ECHO:"
stream.WriteLine "ECHO:"
stream.WriteLine "ECHO: %_count% file(s) successfully copied."
stream.WriteLine "SET _count="
stream.WriteLine "ENDLOCAL"
stream.WriteLine "EXIT /B 0"


' ----------- '
' Script exit '
' ----------- '
On Error GoTo 0
Set fso = Nothing
Set oshell = Nothing
