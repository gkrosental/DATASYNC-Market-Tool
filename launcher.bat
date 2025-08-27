@echo off
echo DATASYNC Market Tool - Quick Launch Scripts
echo.
echo Select an option:
echo 1. Quick Demo (most data without interaction)
echo 2. Console Interface (full interactive experience)  
echo 3. Web Interface (Streamlit app)
echo 4. Run Tests
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting Quick Demo...
    python demo.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting Console Interface...
    python datasync_new.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo Starting Web Interface...
    streamlit run streamlit_launcher.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo Running Tests...
    python test_datasync.py
    pause
) else (
    echo Invalid choice. Please run again.
    pause
)
