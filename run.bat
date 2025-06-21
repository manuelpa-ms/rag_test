@echo off
echo Starting RAG Application...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start the Streamlit app
streamlit run app.py
