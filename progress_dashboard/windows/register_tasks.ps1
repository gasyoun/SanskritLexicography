# Register (or re-register) the two residential Task Scheduler entries that keep
# the PWG->RU dashboards live without a manual start:
#
#   "SL progress dashboard server"  — logon → 127.0.0.1:8765 (5 s local ops)
#   "SL progress live refresh"      — logon → live_refresh daemon (60 s web kitchen)
#
# Pattern matches "SL findings dashboard refresh" (H737): InteractiveToken,
# StartWhenAvailable, explicit WorkingDirectory, RestartOnFailure, no battery block.
# LogonType stays InteractiveToken — "run whether user is logged on or not" needs
# stored credentials typed at the keyboard (GTD @DO if wanted later).
#
# Usage (elevated not required for current-user tasks):
#   powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1
#   powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -Unregister
#   powershell -ExecutionPolicy Bypass -File progress_dashboard\windows\register_tasks.ps1 -StartNow

param(
    [switch]$Unregister,
    [switch]$StartNow,
    [string]$Repo = "C:\Users\user\Documents\GitHub\SanskritLexicography",
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$WinDir = Join-Path $Repo "progress_dashboard\windows"
$ServerCmd = Join-Path $WinDir "run_dashboard_server.cmd"
$RefreshCmd = Join-Path $WinDir "run_live_refresh.cmd"
$UserId = "$env:USERDOMAIN\$env:USERNAME"

if (-not (Test-Path $ServerCmd)) { throw "missing $ServerCmd" }
if (-not (Test-Path $RefreshCmd)) { throw "missing $RefreshCmd" }

$tasks = @(
    @{
        Name = "SL progress dashboard server"
        Description = "H2032 autostart: local PWG->RU ops dashboard at http://127.0.0.1:8765/ (5s poll). Runs at logon; RestartOnFailure. Single-instance via port 8765 check."
        Command = "cmd.exe"
        Arguments = "/c `"$ServerCmd`""
        WorkingDirectory = $WinDir
    },
    @{
        Name = "SL progress live refresh"
        Description = "H2032 autostart: publish progress kitchen to gh-pages/progress/ every 60s while translation artifacts move. --idle-stop 0 (never exit). Residential machine only."
        Command = "cmd.exe"
        Arguments = "/c `"$RefreshCmd`""
        WorkingDirectory = $Repo
    }
)

function Unregister-One([string]$Name) {
    # schtasks prints ERROR to stderr when the task is missing — do not treat as fatal.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    schtasks /Query /TN $Name 2>$null | Out-Null
    $found = ($LASTEXITCODE -eq 0)
    if ($found) {
        Write-Host "Removing task: $Name"
        schtasks /Delete /TN $Name /F 2>$null | Out-Null
    } else {
        Write-Host "Not registered: $Name"
    }
    $ErrorActionPreference = $prev
}

function Register-One($t) {
    $xmlPath = Join-Path $env:TEMP ("sl-task-" + ($t.Name -replace '[^\w\-]', '_') + ".xml")
    # UTF-16 LE required by schtasks /Create /XML
    $xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>$($t.Description)</Description>
    <URI>\$($t.Name)</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>$UserId</UserId>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$UserId</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$($t.Command)</Command>
      <Arguments>$($t.Arguments)</Arguments>
      <WorkingDirectory>$($t.WorkingDirectory)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@
    $utf16 = New-Object System.Text.UnicodeEncoding $false, $true
    [System.IO.File]::WriteAllText($xmlPath, $xml, $utf16)
    Write-Host "Registering: $($t.Name)"
    schtasks /Create /TN $t.Name /XML $xmlPath /F | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "schtasks /Create failed for $($t.Name) (exit $LASTEXITCODE)" }
    Remove-Item $xmlPath -Force -ErrorAction SilentlyContinue
}

if ($Unregister) {
    foreach ($t in $tasks) { Unregister-One $t.Name }
    Write-Host "Done (unregistered)."
    exit 0
}

foreach ($t in $tasks) {
    Unregister-One $t.Name
    Register-One $t
}

if ($StartNow) {
    foreach ($t in $tasks) {
        Write-Host "Starting: $($t.Name)"
        schtasks /Run /TN $t.Name | Out-Host
    }
}

Write-Host ""
Write-Host "Registered under current user ($UserId):"
foreach ($t in $tasks) { Write-Host "  - $($t.Name)" }
Write-Host "Logs: $WinDir\dashboard_server.log , $WinDir\live_refresh_daemon.log"
Write-Host "Re-run with -StartNow to launch immediately without waiting for next logon."
