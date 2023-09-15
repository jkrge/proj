@echo off
setlocal enabledelayedexpansion
for %%f in ("backup\*.zip") do (
	for /f "tokens=4" %%s in ('7z.exe t "%%f" ^| find "Physical Size = "') do (set size=%%s)
	echo Size is !size!
	if !size! leq 10485760 (
	set namef=%%f
	call :errorsize)
	7z.exe t "%%f" 
	echo !errorlevel!
	if !errorlevel! equ 0 (
	echo "%date% %time% File %%f verified successfully" >> logs\info.log
	) else (
	echo "%date% %time% File %%f has an error" >> logs\error.log
	)
	)
	pause
:errorsize
echo "%date% %time% Size of %namef% less than 10MB (%size%!B)"	>> logs\error.log
exit /b
pause