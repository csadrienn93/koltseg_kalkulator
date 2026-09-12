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


if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()

    print("Adatok:", len(adatok), "sor")
    print("Beállítások:", len(beallitasok), "sor")