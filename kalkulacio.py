import pandas as pd
import math
from adatkezeles import excel_adatok_beolvasasa

def anyagkoltseg_szamitas(felhasznalt_alapanyag, anyag_ar):
    return felhasznalt_alapanyag / 1000 * anyag_ar

def beallitas_keresese(beallitasok, parameter_nev):
    for _, sor in beallitasok.iterrows():
        if sor["parameter"] == parameter_nev:
            return sor["ertek"]
    raise ValueError(f"Nem található beállítás: {parameter_nev}")

def energiafogyasztas_becslese(nyomtatasi_ido, nyomtato_fogyasztas):
    nyomtatasi_ido_ora = nyomtatasi_ido / 60
    energiafogyasztas = nyomtatasi_ido_ora * nyomtato_fogyasztas / 1000
    return energiafogyasztas

def energiakoltseg_szamitas(energiafogyasztas, aram_ar):
    return energiafogyasztas * aram_ar

def kozvetlen_koltseg_szamitas(anyagkoltseg, energiakoltseg, csomagolasi_koltseg):
    kozvetlen_koltseg = anyagkoltseg + energiakoltseg + csomagolasi_koltseg
    return kozvetlen_koltseg

def platform_dij_szamitas(eladasi_ar, szallitasi_dij, jutalek_szazalek, helyi_felar_szazalek):
    dijalap = eladasi_ar + szallitasi_dij
    jutalek = dijalap * jutalek_szazalek / 100
    helyi_felar = dijalap * helyi_felar_szazalek / 100
    return jutalek + helyi_felar

def becsult_eredmeny_szamitas(eladasi_ar,termek_kozvetlen_koltsege,platform_dij):
    becsult_eredmeny = (eladasi_ar - termek_kozvetlen_koltsege - platform_dij)
    return becsult_eredmeny

def megteruleshez_szukseges_darabszam(indulo_beruhazas, becsult_eredmeny):
    if indulo_beruhazas <= 0 or becsult_eredmeny <= 0:
        return None
    return math.ceil(indulo_beruhazas / becsult_eredmeny)

# Ha van megadott energiafogyasztás, azt használja, de ha nincs, akkor becsül.
def energiafogyasztas_meghatarozasa(energiafogyasztas, nyomtatasi_ido, nyomtato_fogyasztas):
    if pd.notna(energiafogyasztas) and energiafogyasztas > 0:
        return energiafogyasztas
    return energiafogyasztas_becslese(
        nyomtatasi_ido,
        nyomtato_fogyasztas
    )
def haszonhanyad_szamitas(becsult_eredmeny, eladasi_ar):
    if eladasi_ar <= 0:
        return 0
    haszonhanyad = becsult_eredmeny / eladasi_ar * 100
    return haszonhanyad
    
if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()

    aram_ar = beallitas_keresese(
    beallitasok,
    "villamos_energia_ar"
    )
    nyomtato_fogyasztas = beallitas_keresese(
    beallitasok,
    "nyomtato_fogyasztas"
    )
    platform_jutalek = beallitas_keresese(
    beallitasok,
    "platform_jutalek"
    )
    platform_helyi_felar = beallitas_keresese(
    beallitasok,
    "platform_helyi_felar"
    )
    havi_fix_koltseg = beallitas_keresese(
    beallitasok,
    "havi_fix_koltseg"
    )
   
    adatok["anyagkoltseg"] = adatok.apply(
    lambda sor: anyagkoltseg_szamitas(
        sor["felhasznalt_alapanyag"],
        sor["anyag_ar"]
        ),
    axis=1
    )
    adatok["felhasznalt_energia"] = adatok.apply(
    lambda sor: energiafogyasztas_meghatarozasa(
        sor["energiafogyasztas"],
        sor["nyomtatasi_ido"],
        nyomtato_fogyasztas
        ),
    axis=1
    )
    adatok["energiakoltseg"] = adatok.apply(
    lambda sor: energiakoltseg_szamitas(
        sor["felhasznalt_energia"],
        aram_ar
        ),
    axis=1
    )
    adatok["termek_kozvetlen_koltsege"] = adatok.apply(
    lambda sor: kozvetlen_koltseg_szamitas(
        sor["anyagkoltseg"],
        sor["energiakoltseg"],
        sor["csomagolasi_koltseg"]
        ),
    axis=1
    )
    adatok["platform_dij"] = adatok.apply(
        lambda sor: platform_dij_szamitas(
            sor["eladasi_ar"],
            sor.get("szallitasi_dij", 0),
            platform_jutalek,
            platform_helyi_felar
        ),
    axis=1
    )

    adatok["becsult_eredmeny"] = adatok.apply(
    lambda sor: becsult_eredmeny_szamitas(
        sor["eladasi_ar"],
        sor["termek_kozvetlen_koltsege"],
        sor["platform_dij"]
        ),
         axis=1
    )
    adatok["haszonhanyad"] = adatok.apply(
        lambda sor: haszonhanyad_szamitas(
            sor["becsult_eredmeny"],
            sor["eladasi_ar"]
        ),
        axis=1
    )

    print("\nKalkuláció eredménye:")
    print(f"Termék: {adatok['termek'].iloc[0]}")
    print(f"Selejt: {adatok['selejt'].iloc[0]:g} db")
    print(f"Felhasznált alapanyag: "f"{adatok['felhasznalt_alapanyag'].iloc[0]:g} g")
    print(f"Alapanyag ára: "f"{adatok['anyag_ar'].iloc[0]:g} Ft/kg")
    print(f"Nyomtatási idő: "f"{adatok['nyomtatasi_ido'].iloc[0]:g} perc")
    print(f"Felhasznált energia: "f"{adatok['felhasznalt_energia'].iloc[0]:.2f} kWh")
    print(f"Anyagköltség: "f"{adatok['anyagkoltseg'].iloc[0]:.0f} Ft")
    print(f"Energiaköltség: "f"{adatok['energiakoltseg'].iloc[0]:.0f} Ft")
    print(f"Közvetlen költség: "f"{adatok['termek_kozvetlen_koltsege'].iloc[0]:.0f} Ft")
    print(f"Eladási ár: "f"{adatok['eladasi_ar'].iloc[0]:g} Ft")
    print(f"Platformdíj: "f"{adatok['platform_dij'].iloc[0]:.0f} Ft")
    print(f"Becsült eredmény: "f"{adatok['becsult_eredmeny'].iloc[0]:.0f} Ft")
    print(f"Haszonhányad: "f"{adatok['haszonhanyad'].iloc[0]:.1f}%")