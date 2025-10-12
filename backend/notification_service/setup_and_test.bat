@echo off
echo ================================================
echo Notification Service - Setup and Test
echo ================================================
echo.

REM Step 1: Check if we're in the right directory
echo [Step 1] Checking directory...
if not exist "app\__init__.py" (
    echo ERROR: Not in notification_service directory!
    echo Current directory: %CD%
    pause
    exit /b 1
)
echo ✓ In correct directory
echo.

REM Step 2: Install all dependencies
echo [Step 2] Installing dependencies...
pip install Flask Flask-CORS Flask-SQLAlchemy python-dotenv pika requests psycopg2-binary APScheduler pytest pytest-cov coverage
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All dependencies installed
echo.

REM Step 3: Check test directory structure
echo [Step 3] Checking test directory...
if not exist "test" (
    echo Creating test directory...
    mkdir test
)

if not exist "test\__init__.py" (
    echo Creating test\__init__.py...
    type nul > test\__init__.py
)

REM Check for test files
if exist "test\test.py" (
    echo Found test\test.py - Renaming to test_notification_service.py...
    move test\test.py test\test_notification_service.py
)

if not exist "test\test_notification_service.py" (
    echo ERROR: test_notification_service.py not found in test directory!
    echo Please create the test file first.
    pause
    exit /b 1
)
echo ✓ Test directory structure is correct
echo.

REM Step 4: Verify imports
echo [Step 4] Verifying imports...
python -c "import flask; import apscheduler; import pika; print('✓ All imports successful')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Some imports failed
    pause
    exit /b 1
)
echo.

REM Step 5: Run tests
echo [Step 5] Running tests...
echo ------------------------------------------------
python -m unittest discover -s test -p "test_*.py" -v
echo ------------------------------------------------
echo.

if %ERRORLEVEL% NEQ 0 (
    echo Some tests failed. Review the output above.
    echo.
) else (
    echo ✓ All tests passed!
    echo.
)

REM Step 6: Generate coverage report
echo [Step 6] Generating coverage report...
coverage run -m unittest discover -s test -p "test_*.py"
echo.
echo Coverage Summary:
echo ------------------------------------------------
coverage report
echo ------------------------------------------------
echo.

REM Step 7: Generate HTML coverage
echo [Step 7] Generating HTML coverage report...
coverage html
echo ✓ HTML report saved to: htmlcov\index.html
echo.

echo ================================================
echo Setup and Testing Complete!
echo ================================================
echo.
echo To view detailed coverage:
echo   start htmlcov\index.html
echo.

set /p OPEN="Open coverage report now? (y/n): "
if /i "%OPEN%"=="y" start htmlcov\index.html

pause