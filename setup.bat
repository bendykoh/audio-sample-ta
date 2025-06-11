@echo off
setlocal

:: Set environment name
set ENV_NAME=audio-sample-env

:: Check if conda is installed
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Conda is not installed. Please install Conda first.
    exit /b 1
)

:: Remove environment if it exists
call conda env remove -n %ENV_NAME% --yes

:: Create new environment with Python 3.12
echo Creating new Conda environment '%ENV_NAME%' with Python 3.12...
call conda create -n %ENV_NAME% python=3.12 --yes

:: Create a separate script for package installation
(
echo @echo off
echo call conda activate %ENV_NAME%
echo pip install -r backend/requirements.txt
echo pause
) > install_packages.bat

echo.
echo Environment created successfully!
echo.
echo Please run 'install_packages.bat' to install the required packages
echo.
echo To activate the environment manually, use:
echo     conda activate %ENV_NAME%
echo.
echo To deactivate when you're done:
echo     conda deactivate

endlocal