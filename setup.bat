@echo off
echo Setting up RAG Application...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run setup script
python setup.py

echo.
echo Setup complete! To run the application:
echo   streamlit run app.py
echo.
pause
