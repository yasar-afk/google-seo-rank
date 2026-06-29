"""
Google Siralama Takipcisi
Google Custom Search API ile calisir.
Ucretsiz: Gunluk 100 sorgu
"""

import os
import sys
import re
import time
import argparse
import datetime
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

import requests
import pandas as pd
from halo import Halo
from termcolor import colored

from config import (
    VARSAYILAN_KELIME,
    VARSAYILAN_SITEM,
    VARSAYILAN_RAKIPLER,
    API_ZAMAN_ASIMI,
    API_MAX_DENEME,
    API_BEKLEME_SURESI,
)

# Logging ayarlari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class AramaSonucu:
    """Tek bir arama sonucu"""

    anahtar_kelime: str
    sira: int
    url: str
    baslik: str
    tarih: str
    tur: str


class APIHatasi(Exception):
    """API ile ilgili hatalar icin"""


class SiralamaTakipci:
    """Google siralama takip sinifi"""

    MAX_DENEME = API_MAX_DENEME
    BEKLEME_SURESI = API_BEKLEME_SURESI

    def __init__(self, api_anahtari: str, cse_id: str):
        self.spinner = Halo(text="", spinner="dots")
        self.api_anahtari = api_anahtari
        self.cse_id = cse_id

    def google_ara(
        self, anahtar_kelime: str, baslangic: int = 1
    ) -> list[dict]:
        """Google Custom Search API ile arama yapar"""
        url = "https://www.googleapis.com/customsearch/v1"
        parametreler = {
            "key": self.api_anahtari,
            "cx": self.cse_id,
            "q": anahtar_kelime,
            "start": baslangic,
            "num": 10,
        }

        for deneme in range(1, self.MAX_DENEME + 1):
            try:
                yanit = requests.get(url, params=parametreler, timeout=API_ZAMAN_ASIMI)

                if yanit.status_code == 200:
                    veri = yanit.json()
                    if "items" in veri:
                        return veri["items"]
                    return []

                if yanit.status_code == 429:
                    bekleme = self.BEKLEME_SURESI * deneme
                    logger.warning(
                        f"  API limit asimi, {bekleme}s bekleniyor... "
                        f"(Deneme {deneme}/{self.MAX_DENEME})"
                    )
                    time.sleep(bekleme)
                    continue

                if yanit.status_code == 403:
                    raise APIHatasi("API anahtari veya CSE ID yanlis")

                logger.error(
                    f"  API hatasi: HTTP {yanit.status_code}"
                )
                return []

            except requests.exceptions.Timeout:
                logger.warning(
                    f"  Zaman asimi, tekrar deneme {deneme}/{self.MAX_DENEME}"
                )
                if deneme < self.MAX_DENEME:
                    time.sleep(self.BEKLEME_SURESI)
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"  Baglanti hatasi, tekrar deneme {deneme}/{self.MAX_DENEME}"
                )
                if deneme < self.MAX_DENEME:
                    time.sleep(self.BEKLEME_SURESI)
            except APIHatasi:
                raise
            except Exception as e:
                logger.error(f"  Beklenmeyen hata: {e}")
                return []

        logger.error("  Maksimum deneme sayisina ulasildi")
        return []

    def siralama_kontrol(
        self,
        hedef_url: str,
        sonuclar: list[dict],
        anahtar_kelime: str,
        site_turu: str,
    ) -> list[AramaSonucu]:
        """Belirli bir URL'nin siralamasini bulur"""
        bulunanlar = []

        for i, sonuc in enumerate(sonuclar, 1):
            url = sonuc.get("link", "")
            if hedef_url in url:
                tarih = datetime.date.today().strftime("%d-%m-%Y")
                baslik = sonuc.get("title", "")
                bulunanlar.append(
                    AramaSonucu(anahtar_kelime, i, url, baslik, tarih, site_turu)
                )
                break

        return bulunanlar

    def analiz_et(
        self,
        anahtar_kelime: str,
        benim_sitem: str,
        rakipler: list[str],
    ) -> pd.DataFrame:
        """Ana analiz fonksiyonu"""
        print(
            colored(
                f"\n>> '{anahtar_kelime}' icin siralamalar kontrol ediliyor...",
                "blue",
                attrs=["bold"],
            )
        )

        tum_sonuclar = []

        for baslangic in [1, 11, 21]:
            aralik = f"{baslangic}-{baslangic + 9}"
            print(colored(f"  >> {aralik} arasi sonuclar aliniyor...", "cyan"))
            sonuclar = self.google_ara(anahtar_kelime, baslangic)
            tum_sonuclar.extend(sonuclar)
            if baslangic < 21:
                time.sleep(0.5)

        if not tum_sonuclar:
            print(colored("  !! Sonuc bulunamadi", "red"))
            return pd.DataFrame(
                columns=["AnahtarKelime", "Sira", "URL", "Baslik", "Tarih", "Tur"]
            )

        print(colored(f"  >> Toplam {len(tum_sonuclar)} sonuc bulundu", "green"))

        tum_bulunanlar = []

        # Sitemizin siralamasini bul
        benim_sonuclari = self.siralama_kontrol(
            benim_sitem, tum_sonuclar, anahtar_kelime, "Benim Sitem"
        )
        tum_bulunanlar.extend(benim_sonuclari)

        # Rakiplerin siralamasini bul
        for rakip in rakipler:
            rakip_sonuclari = self.siralama_kontrol(
                rakip, tum_sonuclar, anahtar_kelime, "Rakip"
            )
            tum_bulunanlar.extend(rakip_sonuclari)

        if not tum_bulunanlar:
            return pd.DataFrame(
                columns=["AnahtarKelime", "Sira", "URL", "Baslik", "Tarih", "Tur"]
            )

        df = pd.DataFrame(
            [
                {
                    "AnahtarKelime": s.anahtar_kelime,
                    "Sira": s.sira,
                    "URL": s.url,
                    "Baslik": s.baslik,
                    "Tarih": s.tarih,
                    "Tur": s.tur,
                }
                for s in tum_bulunanlar
            ]
        )

        return df.sort_values(by="Sira").reset_index(drop=True)

    def excel_kaydet(self, anahtar_kelime: str, df: pd.DataFrame) -> Optional[str]:
        """Sonuclari Excel'e kaydeder"""
        guvenli_isim = re.sub(r"[^\w\s-]", "", anahtar_kelime)
        guvenli_isim = re.sub(r"\s+", "_", guvenli_isim)
        dosya_adi = f"{guvenli_isim}_siralama.xlsx"

        try:
            with pd.ExcelWriter(dosya_adi, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Siralama")

                # Sutun genisliklerini ayarla
                worksheet = writer.sheets["Siralama"]
                sutun_genislikleri = {
                    "A": 20,  # AnahtarKelime
                    "B": 8,   # Sira
                    "C": 50,  # URL
                    "D": 40,  # Baslik
                    "E": 15,  # Tarih
                    "F": 15,  # Tur
                }
                for sutun, genislik in sutun_genislikleri.items():
                    worksheet.column_dimensions[sutun].width = genislik

            print(colored(f"\nOK Kaydedildi: {dosya_adi}", "green"))
            return dosya_adi
        except Exception as e:
            print(colored(f"\nHATA Kayit hatasi: {e}", "red"))
            return None

    def csv_kaydet(self, anahtar_kelime: str, df: pd.DataFrame) -> Optional[str]:
        """Sonuclari CSV'ye kaydeder"""
        guvenli_isim = re.sub(r"[^\w\s-]", "", anahtar_kelime)
        guvenli_isim = re.sub(r"\s+", "_", guvenli_isim)
        dosya_adi = f"{guvenli_isim}_siralama.csv"

        try:
            df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
            print(colored(f"OK CSV kaydedildi: {dosya_adi}", "green"))
            return dosya_adi
        except Exception as e:
            print(colored(f"HATA CSV kayit hatasi: {e}", "red"))
            return None


def ayarlari_yukle() -> tuple[str, str]:
    """API ayarlarini yukler"""
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

    return api_anahtari, cse_id


def argumanlari_ayir() -> argparse.Namespace:
    """Komut satiri argumanlarini ayirir"""
    parser = argparse.ArgumentParser(
        description="Google Siralama Takipcisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  python rank_tracker.py
  python rank_tracker.py -k "running shoes"
  python rank_tracker.py -k "running shoes" -s "https://adidas.com"
  python rank_tracker.py -k "running shoes" -r "nike.com" "reebok.com"
  python rank_tracker.py -k "running shoes" --csv
        """,
    )

    parser.add_argument(
        "-k", "--kelime",
        help="Aranacak anahtar kelime",
    )
    parser.add_argument(
        "-s", "--sitem",
        help="Kendi sitenizin URL'si",
    )
    parser.add_argument(
        "-r", "--rakipler",
        nargs="+",
        help="Rakip sitelerin URL'leri (boslukla ayirarak)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Ayni zamanda CSV olarak da kaydet",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ayrintili cikti goster",
    )

    return parser.parse_args()


def main():
    """Ana program"""
    args = argumanlari_ayir()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # API ayarlarini yukle
    api_anahtari, cse_id = ayarlari_yukle()

    # Varsayilan degerler
    anahtar_kelime = args.kelime or VARSAYILAN_KELIME
    benim_sitem = args.sitem or VARSAYILAN_SITEM
    rakipler = args.rakipler or VARSAYILAN_RAKIPLER

    # Baslik
    print(colored("\n" + "=" * 50, "cyan"))
    print(colored("  GOOGLE SIRALAMA TAKIPCISI", "cyan", attrs=["bold"]))
    print(colored("=" * 50, "cyan"))
    print(colored(f"  Anahtar Kelime : {anahtar_kelime}", "white"))
    print(colored(f"  Sitem          : {benim_sitem}", "white"))
    print(colored(f"  Rakip Sayisi   : {len(rakipler)}", "white"))
    print(colored("=" * 50, "cyan"))

    # Analiz
    takipci = SiralamaTakipci(api_anahtari, cse_id)
    takipci.spinner.start()

    sonuclar = takipci.analiz_et(anahtar_kelime, benim_sitem, rakipler)

    takipci.spinner.stop_and_persist(symbol="*", text="Analiz tamamlandi!")

    # Sonuclari goster
    print(colored("\n" + "=" * 50, "cyan"))
    print(colored("SONUCLAR", "cyan", attrs=["bold"]))
    print(colored("=" * 50, "cyan"))

    if not sonuclar.empty:
        print(sonuclar.to_string(index=False))
    else:
        print("Sonuc bulunamadi")

    # Excel'e kaydet
    takipci.excel_kaydet(anahtar_kelime, sonuclar)

    # CSV'ye kaydet (eger istenirse)
    if args.csv:
        takipci.csv_kaydet(anahtar_kelime, sonuclar)

    print(colored("\nIslem tamamlandi!", "green", attrs=["bold"]))


if __name__ == "__main__":
    main()
