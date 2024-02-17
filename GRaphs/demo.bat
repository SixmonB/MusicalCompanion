@echo off
:menu
cls
echo MENU:
echo 1. Demo 1 : Metronome
echo 2. Demo 2 : Drums + Hihats
echo 3. Demo 3 : Beat + Melody
echo 4. Demo 4 : Beat + Melody + User
echo 5. Exit
echo.


choice /c 12345 /n /m "Enter your choice: "

if errorlevel 5 goto exit

if errorlevel 4 (
	set "file=demos\demo4.json"
	goto run_python
)

if errorlevel 3 (
	echo Running Configuration Window
	python config_window.py
	REM Wait for the first program to finish
	echo.
	echo Configuration has finishied. Press any key to continue...
	pause >nul
	set "file=demos\demo3.json"
	goto run_python
)

if errorlevel 2 (
	set "file=demos\demo2.json"
	goto run_python
)

if errorlevel 1 (
	set "file=demos\demo1.json"
	goto run_python
)


:run_python
echo Running Scheduler
python Gui.py "%file%"

echo.
echo Press any key to continue...
pause >nul
taskkill /f /im python.exe >nul 2>&1 REM Kill the python process
goto menu

:exit