from pathlib import Path
import pandas as pd

ADATFAJL = Path(__file__).parent / "adatok" / "termekadatok.xlsx"


def excel_adatok_beolvasasa():

    adatok = pd.read_excel(
        ADATFAJL,
        sheet_name="Adatok"
    )
    beallitasok = pd.read_excel(
        ADATFAJL,
        sheet_name="Beallitasok"
    )
    return adatok, beallitasok

def beallitasok_szotarba(beallitasok):
    return dict(zip(beallitasok["parameter"], beallitasok["ertek"]))

def szakdolgozati_minta(adatok):
    if "szakdolgozat" not in adatok.columns:
        raise ValueError(
            "Hiányzik a 'szakdolgozat' oszlop az Adatok munkalapról."
        )
    return adatok[adatok["szakdolgozat"] == 1].copy()

if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()

    print("Adatok:", len(adatok), "sor")
    print("Beállítások:", len(beallitasok), "sor")

    parameterek = beallitasok_szotarba(beallitasok)
    for nev, ertek in parameterek.items():
        print(f"{nev}: {ertek}")