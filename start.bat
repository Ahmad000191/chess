@echo off
echo ========================================
echo  Chess Beast - Setup and Launch
echo ========================================

REM Install dependencies
pip install -r requirements.txt --quiet

REM Download Stockfish if not present
if not exist "stockfish\stockfish.exe" (
    echo Downloading Stockfish engine...
    python download_stockfish.py
)

echo.
echo Starting Chess Beast at http://localhost:5000
echo Open your browser to http://localhost:5000
echo Press Ctrl+C to stop.
echo.
python app.py
pause
