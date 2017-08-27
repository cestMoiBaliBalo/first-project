option explicit
dim fso, fld, col, fil, fol, filo, fldo, a, e
set fso = CreateObject("Scripting.FileSystemObject")
set fld = fso.GetFolder("C:\Users\Xavier\AppData\Local\Temp")

' Suppression des fichiers temporaires.
set col = fld.Files
on error resume next
For Each fil in col
	set filo = fso.GetFile(fil)
	a = split(filo.Name, ".")
	e = a(Ubound(a))
	if LCase(filo.Name) <> "arecalog.xav" and e <> "bkp" then
		filo.Delete
	end if
Next
on error goto 0

' Suppression des répertoires temporaires.
set col = fld.SubFolders
on error resume next
For Each fol in col
	set fldo = fso.GetFolder(fol)
	if fldo.Name <> "1282856126" then
		fldo.Delete
	end if
Next
on error goto 0
