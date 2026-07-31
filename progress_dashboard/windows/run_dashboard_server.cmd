@echo off
REM Autostart wrapper: local ops dashboard on 127.0.0.1:8765 (5s poll).
REM Registered as Task Scheduler task "SL progress dashboard server" (logon).
REM Single-instance: if the port is already listening, exit 0.

setlocal
set "REPO=C:\Users\user\Documents\GitHub\SanskritLexicography"
set "RT=%REPO%\RussianTranslation"
set "LOGDIR=%REPO%\progress_dashboard\windows"
set "LOG=%LOGDIR%\dashboard_server.log"
set "PY="

if exist "C:\Python314\python.exe" set "PY=C:\Python314\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PY set "PY=python"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Port already in use → another instance is serving; do not start a second one.
netstat -ano | findstr /R /C:":8765 .*LISTENING" >nul 2>&1
if %ERRORLEVEL%==0 (
  echo [%DATE% %TIME%] already listening on 8765 — exit >> "%LOG%"
  exit /b 0
)

cd /d "%RT%"
echo [%DATE% %TIME%] starting dashboard_server.py >> "%LOG%"
"%PY%" -u "src\pilot\dashboard_server.py" --host 127.0.0.1 --port 8765 >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
echo [%DATE% %TIME%] dashboard_server exited rc=%RC% >> "%LOG%"
exit /b %RC%
