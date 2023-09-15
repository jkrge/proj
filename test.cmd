@echo off
setlocal enabledelayedexpansion
for %%f in ("backup\*.zip") do (
	for /f "tokens=4" %%s in ('7z.exe t "%%f" ^| find "Physical Size = "') do (set size=%%s)
	7z.exe t "%%f"
	echo !errorlevel!
	if !errorlevel! equ 0 (
		if !size! geq 10485760 (
	echo "%date% %time% File %%f verified successfully" >> logs\info.log
	) else (
	set namef=%%f
	call :errorsize
	)
	) else (
	echo "%date% %time% File %%f has an error" >> logs\error.log
	)
	)
	exit
:errorsize
echo "%date% %time% Size of %namef% less than 10MB (%size%!B)"	>> logs\error.log
set !errorlevel!=1
exit /b