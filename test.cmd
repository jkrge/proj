@echo off
setlocal enabledelayedexpansion
set folderpath=C:\task\backup
set szpath=C:\task
set logpath=C:\logs
if not exist C:\logs (mkdir C:\logs)
for %%f in ("%folderpath%\*.zip") do (
	for /f "tokens=4" %%s in ('%szpath%\7z.exe t "%%f" ^| find "Physical Size = "') do (set size=%%s)
	%szpath%\7z.exe t "%%f"
	echo !errorlevel!
	if !errorlevel! equ 0 (
		if !size! geq 10485760 (
	echo "%date% %time% File %%f verified successfully" >> %logpath%\info.log
	) else (
	set namef=%%f
	call :errorsize
	)
	) else (
	echo "%date% %time% File %%f has an error" >> %logpath%\error.log
	)
	)
	pause
	exit
:errorsize
echo "%date% %time% Size of %namef% less than 10MB (%size%!B)"	>> %logpath%\error.log
set !errorlevel!=1
exit /b