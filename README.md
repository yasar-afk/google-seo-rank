# Google SEO Analiz Araci

Web sitenizin siralamasini takip eden ve otomatik rakip analizi yapan Python araci.

## Ozellikler

- **Siralama Takipcisi**: Belirli anahtar kelimelerde siralama kontrolu
- **Otomatik Rakip Analizi**: Sadece sitenizi girin, rakipleri ve anahtar kelimeleri otomatik bulsun
- **Rakip Karsilastirmasi**: Rakiplerin stratejilerini analiz eder
- **Siralama Raporu**: Oncelikli anahtar kelimeleri siralar
- Google Custom Search API ile guvenilir sonuclar
- Excel'e disa aktarma

## Kurulum

### 1. Python Kutuphanelerini Kur

```bash
pip install -r requirements.txt
```

### 2. .env Dosyasini Olustur

`.env.example` dosyasini `.env` olarak kopyalayin:

```bash
cp .env.example .env
```

Sonra `.env` dosyasini acin ve kendi degerlerinizi yazin:

```
API_ANAHTARI=AIzaSy...
CSE_ID=a1b2c3d4e...
```

### 3. Google Custom Search API Ayarlari

#### Adim 1: Google Cloud Console'da Proje Olustur

1. https://console.cloud.google.com adresine gidin
2. **New Project** olusturun

#### Adim 2: Custom Search API'yi Etkinlestir

1. **APIs & Services** > **Library**
2. `Custom Search API` arayin ve etkinlestirin

#### Adim 3: API Anahtari Olustur

1. **APIs & Services** > **Credentials**
2. **+ Create credentials** > **API key**

#### Adim 4: Custom Search Engine Olustur

1. https://programmablesearchengine.google.com/controlpanel/create
2. `seo-rank` adinda motor olusturun
3. `*` olarak ayarlayin
4. **Search engine ID**'yi kopyalayin

## Kullanim

### Baslat.bat ile

`baslat.bat`'ye cift tiklayin ve menuyu kullanin:

```
[1] Siralama Takipcisi (belirli anahtar kelimeler)
[2] Otomatik Rakip Analizi (sadece site gir)
[3] Cikis
```

### 1. Siralama Takipcisi

Belirli anahtar kelimelerde siralama kontrolu yapar:

```bash
python rank_tracker.py -k "running shoes" -s "https://adidas.com" -r "nike.com" "reebok.com"
```

### 2. Otomatik Rakip Analizi

Sadece sitenizi girin, program:
- Sitenizin anahtar kelimelerini cikarsin
- Rakip siteleri bulsun
- Rakiplerin stratejilerini analiz etsin
- Oncelikli anahtar kelimeleri gostersin
- Siralama karsilastirmasi yapsin

```bash
python rakip_analiz.py
```

Program calistiktan sonra:
```
Web sitenizi girin: https://adidas.com
```

Sonra otomatik olarak:
- Site analizi
- Rakip bulma
- Rakip analizi
- Karsilastirma
- Siralama kontrolu

## Ciktilar

### Siralama Takipcisi
- `*_siralama.xlsx` - Siralama sonuclari

### Otomatik Rakip Analizi
- `*_rakip_analiz_*.xlsx` - 4 sayfalik detayli rapor:
  - Site Analizi
  - Rakip Analizi
  - Kelime Analizi
  - Siralamalar

## Ornek Analiz

```
Web sitenizi girin: https://adidas.com

>> OTOMATIK RAKIP ANALIZI
  Hedef site: https://adidas.com

  [1/4] Site analiz ediliyor...
    Baslik: Adidas Official Website
    Anahtar Kelimeler: shoes, running, athletic...

  [2/4] Rakip siteler ariyor...
    >> 5 rakip bulundu

  [3/4] Rakip siteler analiz ediliyor...
    >> nike.com analiz ediliyor...
    >> reebok.com analiz ediliyor...

  [4/4] Karsilastirma yapiliyor...

>> ONCELIKLI ANAHTAR KELIMELER:
  - running (rakiplerde 4 kez gecti)
  - marathon (rakiplerde 3 kez gecti)
  - performance (rakiplerde 3 kez gecti)
```

## Ucretsiz Sinir

Google Custom Search API ucretsiz planda:
- Gunluk 100 sorgu
- Aylik 3000 sorgu

## Dosya Yapisi

```
googelseo-rank/
├── rank_tracker.py       # Siralama takipcisi
├── rakip_analiz.py       # Otomatik rakip analizi
├── config.py             # Yapilandirma
├── baslat.bat            # Windows baslatma dosyasi
├── requirements.txt      # Python kutuphaneleri
├── README.md             # Bu dosya
├── .env.example          # Ornek API ayarlari
└── .env                  # API ayarlari (git'e eklenmez)
```
