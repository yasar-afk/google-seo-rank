# 🔍 Google SEO Rank Tracker

Web sitenizin Google sıralamasını takip eden ve otomatik rakip analizi yapan Python tabanlı araç.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
![Google](https://img.shields.io/badge/Google-Search%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

## ✨ Özellikler

| Modül | Açıklama | Durum |
|-------|----------|-------|
| 📊 **Rank Tracker** | Belirli anahtar kelimelerde sıralama kontrolü | ✅ |
| 🤖 **Otomatik Rakip Analizi** | Rakip siteleri otomatik bulma | ✅ |
| 🎯 **Kelime Analizi** | Anahtar kelime çıkarma ve karşılaştırma | ✅ |
| 📈 **Sıralama Raporu** | Öncelikli anahtar kelimeler | ✅ |
| 📊 **Excel Export** | Detaylı Excel raporları | ✅ |
| 📄 **CSV Export** | CSV formatında dışa aktarma | ✅ |

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
# 1. Depoyu klonla
git clone https://github.com/yasar-afk/google-seo-rank.git
cd google-seo-rank

# 2. pip ile kur (önerilen)
pip install .

# Veya bağımlılıkları manuel kur
pip install -r requirements.txt
```

### .env Dosyası

```bash
cp .env.example .env
```

```env
API_ANAHTARI=AIzaSy...
CSE_ID=a1b2c3d4e...
```

### API Ayarları

1. **Google Cloud Console**: https://console.cloud.google.com
   - Yeni proje oluştur
   - Custom Search API'yi etkinleştir
   - API anahtarı oluştur

2. **Custom Search Engine**: https://programmablesearchengine.google.com/controlpanel/create
   - Yeni motor oluştur
   - `*` olarak ayarla
   - Search Engine ID'yi kopyala

## 📊 Kullanım

### 1. Siralama Takipcisi

```bash
# Komut satırından
seo-rank -k "running shoes" -s "https://adidas.com" -r "nike.com" "reebok.com"

# Veya Python ile
python rank_tracker.py -k "running shoes" -s "https://adidas.com"
```

**Parametreler:**
| Parametre | Açıklama |
|-----------|----------|
| `-k` | Anahtar kelime |
| `-s` | Sitenizin URL'i |
| `-r` | Rakip siteler (boşlukla ayırarak) |
| `--csv` | CSV olarak da kaydet |
| `-v` | Detaylı çıktı |

### 2. Otomatik Rakip Analizi

```bash
# Komut satırından
seo-analiz

# Veya Python ile
python rakip_analiz.py
```

**Program otomatik olarak:**
1. Sitenizin meta tag'larını analiz eder
2. Google'da arama yaparak rakip siteleri bulur
3. Rakiplerin de analizini yapar
4. Ortak ve benzersiz kelimeleri çıkarır
5. Öncelikli anahtar kelimeleri belirler
6. Sıralama karşılaştırması yapar

**Örnek:**
```
Web sitenizi girin: https://adidas.com

>> OTOMATIK RAKIP ANALIZI
  Hedef site: https://adidas.com

  [1/4] Site analiz ediliyor...
    Başlık: Adidas Official Website
    Anahtar Kelimeler: shoes, running, athletic...

  [2/4] Rakip siteler arıyor...
    >> 5 rakip bulundu

  [3/4] Rakip siteler analiz ediliyor...
    >> nike.com analiz ediliyor...
    >> reebok.com analiz ediliyor...

  [4/4] Karşılaştırma yapılıyor...

>> ÖNCELİKLI ANAHTAR KELİMELER:
  - running (rakiplerde 4 kez geçti)
  - marathon (rakiplerde 3 kez geçti)
  - performance (rakiplerde 3 kez geçti)
```

## 📊 Çıktılar

### Siralama Takipcisi
- `*_siralama.xlsx` - Sıralama sonuçları
- `*_siralama.csv` - CSV formatı (opsiyonel)

### Otomatik Rakip Analizi
- `*_rakip_analiz_*.xlsx` - 4 sayfalık detaylı rapor:
  - **Sayfa 1**: Site Analizi
  - **Sayfa 2**: Rakip Analizi
  - **Sayfa 3**: Kelime Analizi
  - **Sayfa 4**: Sıralamalar

## 📁 Proje Yapısı

```
google-seo-rank/
├── rank_tracker.py       # Sıralama takipçisi
├── rakip_analiz.py       # Otomatik rakip analizi
├── config.py             # Yapılandırma
├── baslat_tr.bat         # Windows başlatma (Türkçe)
├── start_eng.bat         # Windows başlatma (İngilizce)
├── setup.py              # pip kurulum dosyası
├── pyproject.toml        # Modern Python paketleme
├── requirements.txt      # Python kütüphaneleri
├── README.md             # Bu dosya
├── .env.example          # Örnek API ayarları
└── .env                  # API ayarları (git'e eklenmez)
```

## 🛠️ Teknoloji Stack

| Kategori | Teknoloji |
|----------|-----------|
| **Dil** | Python 3.8+ |
| **API** | Google Custom Search |
| **Web Scraping** | BeautifulSoup4 |
| **Veri** | Pandas |
| **Çıktı** | Excel (openpyxl), CSV |
| **Terminal** | Halo, Termcolor |

## 📋 Gereksinimler

```txt
requests>=2.28.0
pandas>=2.0.0
halo>=0.0.31
termcolor>=2.3.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0
```

## ⚠️ Ücretsiz Sınır

Google Custom Search API ücretsiz planda:
- **Günlük**: 100 sorgu
- **Aylık**: 3000 sorgu

## 🔧 Sorun Giderme

### "API restriction" hatası
Custom Search API'nin etkinleştirildiğinden emin olun.

### "Invalid API key" hatası
API anahtarının doğru kopyalandığından emin olun.

### "Quota exceeded" hatası
Günlük 100 sorgu limitine ulaştıysanız 24 saat bekleyin.

### ".env dosyası bulunamadı" hatası
`.env` dosyasını oluşturun ve API anahtarınızı yazın.

## 📝 Lisans

MIT License

---

**Google SEO Rank Tracker** — MiMoCode tarafından geliştirildi 🔍
