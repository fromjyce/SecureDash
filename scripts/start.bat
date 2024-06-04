@echo off
REM Run the Python script
python "..\data_to_powerbi_main.py"

REM Open the web browser to a specific URL
python -c "import webbrowser; webbrowser.open('{add_power_bi_dashboard_url}')"

REM Pause to keep the window open
pause
