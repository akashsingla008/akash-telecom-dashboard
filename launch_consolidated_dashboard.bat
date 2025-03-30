@echo off
echo === Running Consolidated Telecom Dashboard ===
echo.

rem Check if the consolidated dashboard file exists
if not exist "consolidated_telecom_dashboard_bkup.py" (
    echo Error: consolidated_telecom_dashboard.py not found!
    echo Please download or copy the consolidated dashboard script first.
    echo.
    pause
    exit /b 1
)

rem Check for required packages
echo Checking Python packages...
python -m pip install streamlit pandas matplotlib seaborn plotly pyarrow --upgrade

rem Check for data files
echo.
echo Checking for data files...
if not exist "output\" mkdir output
dir /b output\*.csv 2>nul | find /v "" >nul
if %errorlevel% neq 0 (
    echo No data files found in output directory.
    if exist telecom_data_generator.py (
        echo Running data generator...
        python telecom_data_generator.py
    ) else (
        echo Warning: No data generator found. The dashboard may not display properly.
    )
)

echo.
echo Launching consolidated dashboard...
python -m streamlit run consolidated_telecom_dashboard_bkup.py

pause