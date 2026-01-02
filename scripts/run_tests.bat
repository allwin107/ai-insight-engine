@echo off
REM Run tests with coverage

echo 🧪 Running Tests...
echo ====================

REM Run pytest with coverage
pytest tests/ -v --cov --cov-report=term-missing --cov-report=html

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All tests passed!
    echo.
    echo 📊 Coverage report generated: htmlcov/index.html
) else (
    echo.
    echo ❌ Some tests failed!
    exit /b 1
)