@echo off
setlocal
title 常州大学 855 机械设计基础 · 真题题库
cd /d "%~dp0常大真题电子版"

if not exist "web\index.html" (
  echo [错误] 未找到 web\index.html
  echo 请把本文件放在与 web 文件夹同一目录下。
  pause
  exit /b 1
)

set "PY="
where python >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
  where py >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY goto NOPYTHON

set "PORTFILE=%TEMP%\cx855_port.txt"
del "%PORTFILE%" >nul 2>nul
%PY% -c "import socket,pathlib; s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); pathlib.Path(r'%TEMP%\cx855_port.txt').write_text(str(p))"
if errorlevel 1 goto NOPYTHON
if not exist "%PORTFILE%" goto NOPYTHON

for /f %%p in ('type "%PORTFILE%"') do set "PORT=%%p"
del "%PORTFILE%" >nul 2>nul
if "%PORT%"=="" goto NOPYTHON

echo.
echo   正在启动本地服务：http://127.0.0.1:%PORT%/
echo   浏览器会自动打开题库页面。
echo   关闭“855题库服务”窗口即可停止服务。
echo.

start "855题库服务（关闭此窗口即停止）" cmd /k %PY% -m http.server %PORT% --directory "web"
timeout /t 2 >nul
start "" "http://127.0.0.1:%PORT%/"
timeout /t 3 >nul
exit /b 0

:NOPYTHON
echo.
echo   未检测到可用的 Python，改为直接打开本地文件。
echo   提示：直接打开时功能完全可用；安装 Python 后可启用本地服务。
echo.
start "" "web\index.html"
exit /b 0
