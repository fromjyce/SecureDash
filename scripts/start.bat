@echo off
REM Run the Python script
python "..\data_to_powerbi_main.py"

REM Open the web browser to a specific URL
python -c "import webbrowser; webbrowser.open('https://app.powerbi.com/groups/me/dashboards/1b1a4654-3041-4154-b269-cad399473e79?experience=power-bi')"

REM Pause to keep the window open
pause
