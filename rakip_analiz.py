"""
Otomatik Rakip Analiz Sistemi
Verilen web sitesinin rakiplerini bulur, anahtar kelimeleri cikarir
ve siralama karsilastirmasi yapar.
"""

import os
import re
import time
import sys
import logging
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter

import requests
from bs4 import BeautifulSoup
import pandas as pd
from halo import Halo
from termcolor import colored
from dotenv import load_dotenv

from config import API_ZAMAN_ASIMI, API_MAX_DENEME, API_BEKLEME_SURESI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class SiteAnalizi:
    """Bir web sitesinin analiz sonucu"""

    url: str
    baslik: str = ""
    aciklama: str = ""
    anahtar_kelimeler: list[str] = field(default_factory=list)
    icerik_kelimeleri: list[str] = field(default_factory=list)


@dataclass
class RakipAnalizi:
    """Rakip analiz sonucu"""

    site: SiteAnalizi
    ortak_kelimeler: list[str] = field(default_factory=list)
    benzersiz_kelimeler: list[str] = field(default_factory=list)


class WebAnalizci:
    """Web sitelerini analiz eden sinif"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def siteyi_analiz_et(self, url: str) -> Optional[SiteAnalizi]:
        """Bir web sitesini analiz eder"""
        try:
            # URL duzeltme
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            yanit = requests.get(url, headers=self.HEADERS, timeout=15)
            yanit.raise_for_status()

            soup = BeautifulSoup(yanit.text, "html.parser")

            # Baslik
            baslik = ""
            if soup.title and soup.title.string:
                baslik = soup.title.string.strip()

            # Meta aciklama
            aciklama = ""
            meta_aciklama = soup.find("meta", attrs={"name": "description"})
            if meta_aciklama and meta_aciklama.get("content"):
                aciklama = meta_aciklama["content"].strip()

            # Meta anahtar kelimeler
            anahtar_kelimeler = []
            meta_kelimeler = soup.find("meta", attrs={"name": "keywords"})
            if meta_kelimeler and meta_kelimeler.get("content"):
                kelimeler = meta_kelimeler["content"].split(",")
                anahtar_kelimeler = [k.strip().lower() for k in kelimeler if k.strip()]

            # Icerik kelimeleri (baslik ve paragraflardan)
            icerik_kelimeleri = []
            for etiket in ["h1", "h2", "h3", "p", "span"]:
                for bulunan in soup.find_all(etiket):
                    if bulunan.string:
                        kelimeler = self._kelime_ayir(bulunan.string)
                        icerik_kelimeleri.extend(kelimeler)

            return SiteAnalizi(
                url=url,
                baslik=baslik,
                aciklama=aciklama,
                anahtar_kelimeler=anahtar_kelimeler,
                icerik_kelimeleri=icerik_kelimeleri,
            )

        except Exception as e:
            logger.error(f"  Site analiz hatasi ({url}): {e}")
            return None

    def _kelime_ayir(self, metin: str) -> list[str]:
        """Metni kelimelere ayirir ve temizler"""
        # Turkce ve Ingilizce stop kelimeler
        stop_kelimeler = {
            "ve", "ile", "bir", "bu", "o", "da", "de", "mi", "mu",
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "for", "with", "about", "against", "between", "through",
            "during", "before", "after", "above", "below", "to", "from",
            "up", "down", "in", "out", "on", "off", "over", "under",
            "again", "further", "then", "once", "here", "there", "when",
            "where", "why", "how", "all", "both", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "s", "t", "don",
            "now",
        }

        # Temizleme
        metin = metin.lower()
        metin = re.sub(r"[^\w\s]", " ", metin)
        kelimeler = metin.split()

        # Stop kelimeleri ve kisa kelimeleri cikar
        return [
            k for k in kelimeler
            if k not in stop_kelimeler and len(k) > 2
        ]


class RakipBulucu:
    """Rakip siteleri bulan sinif"""

    def __init__(self, api_anahtari: str, cse_id: str):
        self.api_anahtari = api_anahtari
        self.cse_id = cse_id

    def rakip_bul(self, site_url: str, max_rakip: int = 5) -> list[str]:
        """Google'da arama yaparak rakip siteleri bulur"""
        # Site URL'sinden domain adini cikar
        domain = site_url.replace("https://", "").replace("http://", "")
        domain = domain.split("/")[0]

        # Google'da "site: ile ilgili" aramasi yap
        sorgu = f"site related to {domain}"

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            parametreler = {
                "key": self.api_anahtari,
                "cx": self.cse_id,
                "q": sorgu,
                "num": 10,
            }

            yanit = requests.get(url, params=parametreler, timeout=API_ZAMAN_ASIMI)

            if yanit.status_code == 200:
                veri = yanit.json()
                if "items" in veri:
                    rakipler = []
                    for item in veri["items"]:
                        link = item.get("link", "")
                        # Kendi sitesini cikar
                        if domain not in link:
                            # Domain'i al
                            rakip_domain = link.split("/")[2]
                            if rakip_domain not in [r.split("/")[0] for r in rakipler]:
                                rakipler.append(link)
                                if len(rakipler) >= max_rakip:
                                    break
                    return rakipler

            # Eger API basarisiz olursa, bilinen rakipleri don
            return self._varsayilan_rakipler(domain)

        except Exception as e:
            logger.error(f"  Rakip bulma hatasi: {e}")
            return self._varsayilan_rakipler(domain)

    def _varsayilan_rakipler(self, domain: str) -> list[str]:
        """API calismazsa varsayilan rakip listesi"""
        # Domain bazinda varsayilan rakipler
        rakip_haritasi = {
            "adidas.com": ["nike.com", "reebok.com", "asics.com", "hoka.com"],
            "nike.com": ["adidas.com", "puma.com", "newbalance.com", "underarmour.com"],
            "google.com": ["bing.com", "yahoo.com", "duckduckgo.com"],
        }

        for key, degerler in rakip_haritasi.items():
            if key in domain:
                return [f"https://www.{r}" for r in degerler]

        return []


class SiralamaKontrolcu:
    """Siralama kontrolu yapan sinif"""

    def __init__(self, api_anahtari: str, cse_id: str):
        self.api_anahtari = api_anahtari
        self.cse_id = cse_id

    def siralama_kontrol(self, anahtar_kelime: str, hedef_url: str) -> int:
        """Belirli bir anahtar kelime icin siralamayi kontrol eder"""
        try:
            # Domain adini al
            domain = hedef_url.replace("https://", "").replace("http://", "")
            domain = domain.split("/")[0]

            url = "https://www.googleapis.com/customsearch/v1"
            parametreler = {
                "key": self.api_anahtari,
                "cx": self.cse_id,
                "q": anahtar_kelime,
                "num": 10,
            }

            yanit = requests.get(url, params=parametreler, timeout=API_ZAMAN_ASIMI)

            if yanit.status_code == 200:
                veri = yanit.json()
                if "items" in veri:
                    for i, item in enumerate(veri["items"], 1):
                        link = item.get("link", "")
                        if domain in link:
                            return i

            return -1  # Bulunamadi

        except Exception as e:
            logger.error(f"  Siralama kontrol hatasi: {e}")
            return -1


class OtomatikRakipAnalizci:
    """Otomatik rakip analiz sistemi"""

    def __init__(self, api_anahtari: str, cse_id: str):
        self.spinner = Halo(text="", spinner="dots")
        self.web_analizci = WebAnalizci()
        self.rakip_bulucu = RakipBulucu(api_anahtari, cse_id)
        self.siralama_kontrolcu = SiralamaKontrolcu(api_anahtari, cse_id)

    def analiz_et(self, site_url: str) -> dict:
        """Tam analiz yapar"""
        print(colored("\n>> OTOMATIK RAKIP ANALIZI", "blue", attrs=["bold"]))
        print(colored(f"  Hedef site: {site_url}", "cyan"))

        # 1. Siteyi analiz et
        print(colored("\n  [1/4] Site analiz ediliyor...", "yellow"))
        site_analizi = self.web_analizci.siteyi_analiz_et(site_url)
        if not site_analizi:
            print(colored("  !! Site analiz edilemedi", "red"))
            return {}

        self._site_bilgisi_goster(site_analizi)

        # 2. Rakip siteleri bul
        print(colored("\n  [2/4] Rakip siteler ariyor...", "yellow"))
        rakip_url_leri = self.rakip_bulucu.rakip_bul(site_url)
        print(colored(f"  >> {len(rakip_url_leri)} rakip bulundu", "green"))

        # 3. Rakipleri analiz et
        print(colored("\n  [3/4] Rakip siteler analiz ediliyor...", "yellow"))
        rakip_analizleri = []
        for rakip_url in rakip_url_leri:
            print(colored(f"  >> {rakip_url} analiz ediliyor...", "cyan"))
            analiz = self.web_analizci.siteyi_analiz_et(rakip_url)
            if analiz:
                rakip_analizleri.append(analiz)
            time.sleep(0.5)

        # 4. Karsilastirma yap
        print(colored("\n  [4/4] Karsilastirma yapiliyor...", "yellow"))
        sonuclar = self._karsilastirma_yap(site_analizi, rakip_analizleri)

        return sonuclar

    def _site_bilgisi_goster(self, analiz: SiteAnalizi):
        """Site bilgilerini gosterir"""
        print(colored("\n  Site Bilgileri:", "cyan", attrs=["bold"]))
        print(f"    Baslik: {analiz.baslik[:50]}...")
        print(f"    Aciklama: {analiz.aciklama[:50]}...")
        if analiz.anahtar_kelimeler:
            print(f"    Anahtar Kelimeler: {', '.join(analiz.anahtar_kelimeler[:5])}")

    def _karsilastirma_yap(
        self, site: SiteAnalizi, rakipler: list[SiteAnalizi]
    ) -> dict:
        """Site ile rakipleri karsilastirir"""
        # Tum anahtar kelimeleri topla
        site_kelimeleri = set(site.anahtar_kelimeler + site.icerik_kelimeleri)

        tum_rakip_kelimeleri = []
        for rakip in rakipler:
            rakip_kelimeleri = set(rakip.anahtar_kelimeler + rakip.icerik_kelimeleri)
            tum_rakip_kelimeleri.append(rakip_kelimeleri)

        # Ortak kelimeleri bul
        ortak_kelimeler = set()
        for rakip_kelimeleri in tum_rakip_kelimeleri:
            ortak_kelimeler.update(site_kelimeleri & rakip_kelimeleri)

        # Benzersiz kelimeleri bul (rakiplerde olan ama sitede olmayan)
        benzersiz_rakip = set()
        for rakip_kelimeleri in tum_rakip_kelimeleri:
            benzersiz_rakip.update(rakip_kelimeleri - site_kelimeleri)

        # En cok tekrar eden kelimeleri bul
        kelime_sayaci = Counter()
        for rakip_kelimeleri in tum_rakip_kelimeleri:
            kelime_sayaci.update(rakip_kelimeleri)

        # Oncelikli anahtar kelimeler (rakiplerde cok olan ama bizde az olan)
        oncelikli_kelimeler = []
        for kelime, sayi in kelime_sayaci.most_common(10):
            if kelime not in site_kelimeleri or len(site_kelimeleri) < 3:
                oncelikli_kelimeler.append((kelime, sayi))

        # Sonuclari don
        return {
            "site": site,
            "rakipler": rakipler,
            "ortak_kelimeler": list(ortak_kelimeler)[:20],
            "benzersiz_rakip_kelimeleri": list(benzersiz_rakip)[:20],
            "oncelikli_kelimeler": oncelikli_kelimeler[:10],
        }

    def siralama_raporu_olustur(self, sonuclar: dict) -> pd.DataFrame:
        """Siralamalari kontrol edip rapor olusturur"""
        if not sonuclar:
            return pd.DataFrame()

        site = sonuclar["site"]
        rakipler = sonuclar["rakipler"]
        oncelikli_kelimeler = sonuclar.get("oncelikli_kelimeler", [])

        print(colored("\n>> SIRALAMA KONTROLU", "blue", attrs=["bold"]))

        satirlar = []

        # Oncelikli kelimeleri kontrol et
        for kelime, _ in oncelikli_kelimeler[:5]:  # Ilk 5 kelime
            print(colored(f"  >> '{kelime}' icin siralama kontrol ediliyor...", "cyan"))

            # Sitemizin siralamasi
            benim_siralamam = self.siralama_kontrolcu.siralama_kontrol(kelime, site.url)

            # Rakiplerin siralamalari
            rakip_siralamalari = {}
            for rakip in rakipler[:3]:  # Ilk 3 rakip
                rakip_sira = self.siralama_kontrolcu.siralama_kontrol(kelime, rakip.url)
                rakip_siralamalari[rakip.url] = rakip_sira
                time.sleep(0.3)

            # Sonuclari ekle
            satir = {
                "Anahtar Kelime": kelime,
                "Benim Sitem": f"{benim_siralamam}. sirada" if benim_siralamam > 0 else "Bulunamadi",
            }

            for rakip_url, sira in rakip_siralamalari.items():
                domain = rakip_url.split("/")[2]
                satir[domain] = f"{sira}. sirada" if sira > 0 else "Bulunamadi"

            satirlar.append(satir)

        if not satirlar:
            return pd.DataFrame()

        return pd.DataFrame(satirlar)

    def rapor_kaydet(self, sonuclar: dict, siralama_df: pd.DataFrame):
        """Raporu Excel'e kaydeder"""
        if not sonuclar:
            return

        site = sonuclar["site"]

        # Dosya adi olustur
        domain = site.url.split("/")[2].replace(".", "_")
        tarih = pd.Timestamp.now().strftime("%Y%m%d")
        dosya_adi = f"{domain}_rakip_analiz_{tarih}.xlsx"

        try:
            with pd.ExcelWriter(dosya_adi, engine="openpyxl") as writer:
                # Sayfa 1: Site Analizi
                site_df = pd.DataFrame([{
                    "URL": site.url,
                    "Baslik": site.baslik,
                    "Aciklama": site.aciklama[:200],
                    "Anahtar Kelimeler": ", ".join(site.anahtar_kelimeler[:10]),
                }])
                site_df.to_excel(writer, index=False, sheet_name="Site Analizi")

                # Sayfa 2: Rakip Analizi
                rakip_satirlar = []
                for rakip in sonuclar["rakipler"]:
                    rakip_satirlar.append({
                        "URL": rakip.url,
                        "Baslik": rakip.baslik,
                        "Aciklama": rakip.aciklama[:200],
                        "Anahtar Kelimeler": ", ".join(rakip.anahtar_kelimeler[:10]),
                    })
                if rakip_satirlar:
                    rakip_df = pd.DataFrame(rakip_satirlar)
                    rakip_df.to_excel(writer, index=False, sheet_name="Rakip Analizi")

                # Sayfa 3: Kelime Karsilastirmasi
                kelime_data = {
                    "Ortak Kelimeler": ", ".join(sonuclar.get("ortak_kelimeler", [])[:10]),
                    "Benzersiz Rakip Kelimeleri": ", ".join(sonuclar.get("benzersiz_rakip_kelimeleri", [])[:10]),
                    "Oncelikli Kelimeler": ", ".join([k[0] for k in sonuclar.get("oncelikli_kelimeler", [])[:10]]),
                }
                kelime_df = pd.DataFrame([kelime_data])
                kelime_df.to_excel(writer, index=False, sheet_name="Kelime Analizi")

                # Sayfa 4: Siralama Raporu
                if not siralama_df.empty:
                    siralama_df.to_excel(writer, index=False, sheet_name="Siralamalar")

                # Sutun genislikleri
                for sayfa in writer.sheets:
                    worksheet = writer.sheets[sayfa]
                    for sutun in worksheet.column_dimensions:
                        worksheet.column_dimensions[sutun].width = 30

            print(colored(f"\nOK Rapor kaydedildi: {dosya_adi}", "green"))

        except Exception as e:
            print(colored(f"\nHATA Rapor kayit hatasi: {e}", "red"))


def main():
    """Ana program"""
    load_dotenv()

    api_anahtari = os.getenv("API_ANAHTARI", "")
    cse_id = os.getenv("CSE_ID", "")

    # Eksik alanlari kontrol et
    eksikler = []
    if not api_anahtari or api_anahtari == "AIzaSy...":
        eksikler.append("API_ANAHTARI")
    if not cse_id or cse_id == "a1b2c3d4e...":
        eksikler.append("CSE_ID")

    if eksikler:
        print(colored("\n  HATA: Asagidaki alanlar .env dosyasinda ayarlanmamis!", "red", attrs=["bold"]))
        print()
        for eksik in eksikler:
            print(colored(f"    - {eksik}", "yellow"))
        print()
        print(colored("  .env dosyasini asagidaki formatta duzenleyin:", "cyan"))
        print()
        print(colored("    API_ANAHTARI=AIzaSy... (Google API anahtariniz)", "white"))
        print(colored("    CSE_ID=...            (Google Search Engine ID)", "white"))
        print()
        print(colored("  Almak icin:", "cyan"))
        print(colored("    API: https://console.cloud.google.com → APIs & Services → Credentials", "white"))
        print(colored("    CSE: https://programmablesearchengine.google.com/controlpanel/create", "white"))
        print()
        sys.exit(1)

    # Kullanici girdisi
    print(colored("\n" + "=" * 50, "cyan"))
    print(colored("  OTOMATIK RAKIP ANALIZ ARACI", "cyan", attrs=["bold"]))
    print(colored("=" * 50, "cyan"))

    site_url = input(colored("\n  Web sitenizi girin: ", "yellow")).strip()
    if not site_url:
        print(colored("  HATA: Site URL'si gerekli!", "red"))
        sys.exit(1)

    # Analiz
    analizci = OtomatikRakipAnalizci(api_anahtari, cse_id)
    analizci.spinner.start()

    sonuclar = analizci.analiz_et(site_url)

    analizci.spinner.stop_and_persist(symbol="*", text="Analiz tamamlandi!")

    if not sonuclar:
        print(colored("\nAnaliz sonucu bulunamadi!", "red"))
        return

    # Siralama raporu
    siralama_df = analizci.siralama_raporu_olustur(sonuclar)

    # Raporu goster
    print(colored("\n" + "=" * 50, "cyan"))
    print(colored("ANALIZ RAPORU", "cyan", attrs=["bold"]))
    print(colored("=" * 50, "cyan"))

    if not siralama_df.empty:
        print(siralama_df.to_string(index=False))
    else:
        print("Siralamalar kontrol edilemedi")

    # Oncelikli kelimeler
    if sonuclar.get("oncelikli_kelimeler"):
        print(colored("\n>> ONCELIKLI ANAHTAR KELIMELER:", "yellow", attrs=["bold"]))
        for kelime, sayi in sonuclar["oncelikli_kelimeler"][:5]:
            print(f"  - {kelime} (rakiplerde {sayi} kez gecti)")

    # Kaydet
    analizci.rapor_kaydet(sonuclar, siralama_df)

    print(colored("\nIslem tamamlandi!", "green", attrs=["bold"]))


if __name__ == "__main__":
    main()
