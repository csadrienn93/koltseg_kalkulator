from pathlib import Path
import pandas as pd

ADATFAJL = Path(__file__).parent / "adatok" / "termekadatok.xlsx"


def excel_adatok_beolvasasa():
    # Beolvassa az Excel két munkalapját.

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


if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()

    print("Adatok:", len(adatok), "sor")
    print("Beállítások:", len(beallitasok), "sor")

    parameterek = beallitasok_szotarba(beallitasok)
    for nev, ertek in parameterek.items():
        print(f"{nev}: {ertek}")