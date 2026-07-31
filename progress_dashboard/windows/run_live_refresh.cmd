@echo off
REM Autostart wrapper: progress kitchen live_refresh daemon.
REM Publishes gh-pages/progress/ every 60s while translation artifacts are moving.
REM --idle-stop 0 = never exit when idle (sleep and keep watching).
REM Registered as Task Scheduler task "SL progress live refresh" (logon).

setlocal
set "REPO=C:\Users\user\Documents\GitHub\SanskritLexicography"
set "LOGDIR=%REPO%\progress_dashboard\windows"
set "LOG=%LOGDIR%\live_refresh_daemon.log"
set "PY="
set "PWG_DATA_ROOT=%REPO%"

if exist "C:\Python314\python.exe" set "PY=C:\Python314\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PY set "PY=python"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

cd /d "%REPO%"
echo [%DATE% %TIME%] starting live_refresh.py --idle-stop 0 >> "%LOG%"
"%PY%" -u "progress_dashboard\live_refresh.py" --idle-stop 0 --interval 60 --active-within 900 --data-root "%REPO%" >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
echo [%DATE% %TIME%] live_refresh exited rc=%RC% >> "%LOG%"
exit /b %RC%
