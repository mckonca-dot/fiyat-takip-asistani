@echo off
TITLE Fiyat Takip Robotu Baslatiliyor...
color 0A

echo ===================================================
echo   FIYAT TAKIP SISTEMI BASLATILIYOR (Fiyat Takipçisi)
echo ===================================================
echo.

:: 1. BACKEND (PYTHON) BASLATILIYOR
echo [1/2] Backend (API & Bot) aciliyor...
start "Backend Sunucusu" cmd /k "cd /d C:\Users\mckon\Desktop\FiyatTakipcisi && python -m uvicorn api:app --reload"

:: Biraz bekle ki backend kendine gelsin
timeout /t 5 >nul

:: 2. FRONTEND (REACT) BASLATILIYOR
echo [2/2] Frontend (Arayuz) aciliyor...
start "Frontend Arayuzu" cmd /k "cd /d C:\Users\mckon\Desktop\FiyatTakipcisi\frontend && npm start"

echo.
echo ✅ SISTEM HAZIR!
echo Iki siyah pencere acildi, onlari kapatma.
echo Bot arka planda calisiyor...
timeout /t 5
exit