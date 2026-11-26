@echo off
chcp 65001 > nul
set "SCRIPT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_PATH=%STARTUP_DIR%\OXEN_Power_Guard.vbs"

echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_PATH%"
echo WshShell.CurrentDirectory = "%SCRIPT_DIR%src" >> "%VBS_PATH%"
echo WshShell.Run "pythonw main.py", 0, False >> "%VBS_PATH%"

echo [완료] 이제 컴퓨터를 켤 때마다 OXEN Power Guard가 자동 실행됩니다.
pause
