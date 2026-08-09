# PowerShell Script to register Daily 8:00 AM Email Summarizer in Windows Task Scheduler

$TaskName = "DailyEmailSummarizer"
$AgentDir = $PSScriptRoot
$VenvPython = Join-Path $AgentDir "venv\Scripts\python.exe"
$MainPy = Join-Path $AgentDir "src\main.py"

Write-Host "Registering Windows Scheduled Task: $TaskName ..." -ForegroundColor Cyan

# Trigger: Daily at 8:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00AM"

# Action: Run Python script via venv python.exe
$Action = New-ScheduledTaskAction -Execute $VenvPython -Argument "`"$MainPy`" --now" -WorkingDirectory $AgentDir

# Register Task
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Description "Automated 8:00 AM Email Summarizer Agent for officialhardik2003@gmail.com" -Force

Write-Host "✅ Scheduled Task '$TaskName' registered successfully to run daily at 8:00 AM!" -ForegroundColor Green
