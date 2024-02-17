@echo off

REM Run the configuration window to set the amount of composer ants and decay factor
python config_window.py

REM Wait for the first program to finish
ping 127.0.0.1 -n 5 > nul

REM Run the Scheduler
python Scheduler.py

REM Pause the batch file before exiting
pause