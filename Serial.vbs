option explicit


' ==========
' Constants.
' ==========
const outputFile = "c:\users\xavier\appdata\local\temp\serial.txt"


' ==========
' Variables.
' ==========
dim fso, d, dc, f, line


' ===============
' Main algorithm.
' ===============
set fso = CreateObject("Scripting.FileSystemObject")


' -------------------
' Remove output file.
' -------------------
if fso.FileExists(outputFile) then
    fso.DeleteFile(outputFile)
end if


' ---------------------------
' Retrieve drives properties.
' ---------------------------
set f = fso.OpenTextFile(outputFile, 2, true, 0)

' Header.
' f.WriteLine("DriveLetter" & ";" & "VolumeName" & ";"  & "SerialNumber" & ";" & "Free Space (Kbytes)" & ";" & "Type" & ";" & "Ready")
' f.WriteLine("-----------" & ";" & "----------" & ";" & "-------------" & ";" & "-------------------" & ";" & "----" & ";" & "-----")

' Detail.
set dc = fso.Drives
For Each d in dc
    if d.IsReady then
        line = d.DriveLetter
        ' line = d.DriveLetter & ";" & d.VolumeName
        ' if Len(d.VolumeName) < 8 then
        '     line = line & ";"
        ' end if
        line = line & ";" & d.SerialNumber & ";" & d.FreeSpace/1024
        ' if Len(d.FreeSpace/1024) < 8 then
        '     line = line & ";"
        ' end if
        line = line & ";" & d.DriveType & ";" & d.IsReady
        f.WriteLine(line)
    end if
Next

f.Close