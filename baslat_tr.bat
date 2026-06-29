@echo off
chcp 65001 >nul
title Google SEO Analiz Araci
color 0B

echo.
echo ========================================
echo    GOOGLE SEO ANALIZ ARACI
echo ========================================
echo.

:: Python kontrolu
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi!
    echo.
    echo Python'u indirmek icin: https://www.python.org/downloads/
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    echo.
    pause
    exit /b 1
)

:: Python versiyonu
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYVER=%%a
echo Python versiyonu: %PYVER%

:: Kutuphane kontrolu
echo.
echo Kutuphaneler kontrol ediliyor...
echo.

set KUTUPHANE_HATASI=0

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] requests - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] requests
)

python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] pandas - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] pandas
)

python -c "import halo" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] halo - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] halo
)

python -c "import termcolor" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] termcolor - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] termcolor
)

python -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] openpyxl - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] openpyxl
)

python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] python-dotenv - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] python-dotenv
)

python -c "import bs4" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] beautifulsoup4 - BULUNAMADI
    set KUTUPHANE_HATASI=1
) else (
    echo [OK] beautifulsoup4
)

:: Eksik kutuphane varsa kur
if %KUTUPHANE_HATASI%==1 (
    echo.
    echo Eksik kutuphaneler bulundu, kuruluyor...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo HATA: Kutuphane kurulumu basarisiz!
        echo.
        echo pip komutu calismadiysa Python'u tekrar kurun
        echo ve "Add Python to PATH" secenegini isaretleyin.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Kutuphaneler basariyla kuruldu!
)

echo.
echo ========================================

:: .env dosyasi kontrolu
if not exist .env (
    echo.
    echo HATA: .env dosyasi bulunamadi!
    echo.
    echo Lutfen .env.example dosyasini .env olarak kopyalayin
    echo ve kendi API anahtarinizi yazin.
    echo.
    echo Ornek:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

:: Menu goster
echo.
echo  Hangi analizi yapmak istiyorsunuz?
echo.
echo    [1] Siralama Takipcisi (belirli anahtar kelimeler)
echo    [2] Otomatik Rakip Analizi (sadece site gir)
echo    [3] Cikis
echo.

set /p SECIM="Seciminiz (1/2/3): "

if "%SECIM%"=="1" goto SIRALAMA
if "%SECIM%"=="2" goto RAKIP
if "%SECIM%"=="3" goto CIKIS
echo Gecersiz secim!
pause
goto SIRALAMA

:RAKIP
echo.
echo ========================================
echo    OTOMATIK RAKIP ANALIZI
echo ========================================
echo.
python rakip_analiz.py
goto BITIR

:SIRALAMA
echo.
echo ========================================
echo    SIRALAMA TAKIPCISI
echo ========================================
echo.
echo Bilgileri girin (bos birakirsaniz varsayilan deger kullanilir):
echo.

set /p KELIME="Anahtar kelime [running shoes]: "
set /p SITEM="Web siteniz [https://www.adidas.com/]: "
set /p RAKIP1="Rakip site 1 [https://www.nike.com]: "
set /p RAKIP2="Rakip site 2 [https://www.reebok.com]: "
set /p RAKIP3="Rakip site 3 [https://www.asics.com]: "
set /p RAKIP4="Rakip site 4 [https://www.hoka.com]: "

echo.
echo ========================================
echo    Parametreler:
echo ========================================
echo    Kelime : %KELIME%
echo    Sitem  : %SITEM%
echo    Rakip1 : %RAKIP1%
echo    Rakip2 : %RAKIP2%
echo    Rakip3 : %RAKIP3%
echo    Rakip4 : %RAKIP4%
echo ========================================
echo.

set /p DEVAM="Devam etmek istiyor musunuz? (E/H): "
if /i not "%DEVAM%"=="E" (
    echo Islem iptal edildi.
    pause
    exit /b 0
)

:: Parametreleri olustur
set PARAMetre=

if not "%KELIME%"=="" set PARAMETRE=%PARAMETRE% -k "%KELIME%"
if not "%SITEM%"=="" set PARAMETRE=%PARAMETRE% -s "%SITEM%"

:: Rakipleri ekle
set RAKIPLER=
if not "%RAKIP1%"=="" set RAKIPLER=%RAKIP1%
if not "%RAKIP2%"=="" set RAKIPLER=%RAKIP1% %RAKIP2%
if not "%RAKIP3%"=="" set RAKIPLER=%RAKIP1% %RAKIP2% %RAKIP3%
if not "%RAKIP4%"=="" set RAKIPLER=%RAKIP1% %RAKIP2% %RAKIP3% %RAKIP4%

if not "%RAKIPLER%"=="" set PARAMETRE=%PARAMETRE% -r %RAKIPLER%

echo.
echo Calistiriliyor...
echo.
python rank_tracker.py %PARAMETRE%
goto BITIR

:CIKIS
echo.
echo Hosca kalin!
pause
exit /b 0

:BITIR
echo.

if %errorlevel% equ 0 (
    echo ========================================
    echo    Islem basariyla tamamlandi!
    echo ========================================
) else (
    echo ========================================
    echo    Bir hata olustu!
    echo ========================================
)

echo.
pause
