@echo off
REM Authentication - Push to GitHub Script
REM This script initializes git and pushes the project to GitHub

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║       Authentication - GitHub Push Script                ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo ✅ Git found!
echo.

REM Check if repository is already initialized
if exist .git (
    echo ✅ Repository already initialized
) else (
    echo 📦 Initializing Git repository...
    git init
    echo ✅ Repository initialized
)

echo.
echo 📝 Configuring Git...

REM Configure Git (optional - customize as needed)
git config user.name "Vignesh" 2>nul
git config user.email "Vignesh423@authentication.co.in" 2>nul

echo.
echo 📋 Checking git status...
git status

echo.
echo 📤 Adding all files to staging...
git add .

echo.
echo 💾 Creating initial commit...
git commit -m "Initial commit: Authentication Multi-Factor Authentication System" 2>nul

if errorlevel 1 (
    echo ℹ️  Repository already up to date
) else (
    echo ✅ Commit created successfully
)

echo.
echo 🔗 Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Vignesh-op/Authentication-multi-level-authentication.git

echo.
echo 🚀 Pushing to GitHub...
echo.
echo Note: You may be prompted to enter your GitHub credentials
echo For HTTPS: Enter your GitHub username and personal access token (not password)
echo For SSH: Ensure you have SSH key configured
echo.

git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Push failed!
    echo.
    echo Troubleshooting tips:
    echo 1. Verify your GitHub credentials
    echo 2. Ensure the repository exists on GitHub
    echo 3. Check your internet connection
    echo 4. Try using SSH instead of HTTPS
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS! Your project has been pushed to GitHub!
echo.
echo 📍 Repository URL: https://github.com/Vignesh-op/Authentication-multi-level-authentication
echo.
pause
