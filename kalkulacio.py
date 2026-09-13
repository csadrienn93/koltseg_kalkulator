import pandas as pd
import math

from adatkezeles import excel_adatok_beolvasasa


def anyagkoltseg_szamitas(felhasznalt_alapanyag, anyag_ar, selejt):
    # Kiszámítja az anyagköltséget a selejtes nyomtatásokkal együtt.
    nyomtatasok_szama = selejt + 1
    anyagkoltseg = (
        felhasznalt_alapanyag / 1000
        * anyag_ar
        * nyomtatasok_szama
    )
    return anyagkoltseg


def beallitas_keresese(beallitasok, parameter_nev):
    for _, sor in beallitasok.iterrows():
        if sor["parameter"] == parameter_nev:
            return sor["ertek"]
    raise ValueError(f"Nem található beállítás: {parameter_nev}")

def energiafogyasztas_becslese(nyomtatasi_ido, nyomtato_fogyasztas):
    nyomtatasi_ido_ora = nyomtatasi_ido / 60
    energiafogyasztas = nyomtatasi_ido_ora * nyomtato_fogyasztas / 1000
    return energiafogyasztas

def energiakoltseg_szamitas(energiafogyasztas, aram_ar, selejt):
    nyomtatasok_szama = selejt + 1
    energiakoltseg = (
        energiafogyasztas
        * aram_ar
        * nyomtatasok_szama
    )
    return energiakoltseg

def kozvetlen_koltseg_szamitas(anyagkoltseg, energiakoltseg, csomagolasi_koltseg):
    kozvetlen_koltseg = anyagkoltseg + energiakoltseg + csomagolasi_koltseg
    return kozvetlen_koltseg

def platform_dij_szamitas(eladasi_ar, jutalek_szazalek, minimum_dij, afa_kulcs):
    jutalek = eladasi_ar * jutalek_szazalek / 100
    if jutalek < minimum_dij:
        jutalek = minimum_dij
    platform_dij = jutalek * (1 + afa_kulcs / 100)
    return platform_dij

def fedezet_szamitas(eladasi_ar, termek_kozvetlen_koltsege, platform_dij):
    fedezet = eladasi_ar - termek_kozvetlen_koltsege - platform_dij
    return fedezet

def fedezeti_pont_szamitas(havi_fix_koltseg, fedezet):
    if fedezet <= 0:
        return None
    fedezeti_pont = havi_fix_koltseg / fedezet

    return math.ceil(fedezeti_pont)

# Ha van megadott energiafogyasztás, azt használja, de ha nincs, akkor becsül.
def energiafogyasztas_meghatarozasa(energiafogyasztas, nyomtatasi_ido, nyomtato_fogyasztas):
    if pd.notna(energiafogyasztas):
        return energiafogyasztas
    return energiafogyasztas_becslese(
        nyomtatasi_ido,
        nyomtato_fogyasztas
    )
def platform_dij_szamitas(eladasi_ar, jutalek_szazalek, minimum_dij, afa_kulcs):
    jutalek = eladasi_ar * jutalek_szazalek / 100
    if jutalek < minimum_dij:
        jutalek = minimum_dij
    platform_dij = jutalek * (1 + afa_kulcs / 100)
    return platform_dij


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
    platform_minimum_dij = beallitas_keresese(
    beallitasok,
    "platform_minimum_dij"
    )
    afa_kulcs = beallitas_keresese(
    beallitasok,
    "afa_kulcs"
    )
    havi_fix_koltseg = beallitas_keresese(
    beallitasok,
    "havi_fix_koltseg"
)

   # print("Áram ára:", aram_ar, "Ft/kWh")
   # print("Nyomtató fogyasztása:", nyomtato_fogyasztas, "W")

    adatok["anyagkoltseg"] = adatok.apply(
    lambda sor: anyagkoltseg_szamitas(
        sor["felhasznalt_alapanyag"],
        sor["anyag_ar"],
        sor["selejt"]
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
        aram_ar,
        sor["selejt"]
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
adatok["platform_dij"] = adatok["eladasi_ar"].apply(
    lambda ar: platform_dij_szamitas(
        ar,
        platform_jutalek,
        platform_minimum_dij,
        afa_kulcs
    )
)
adatok["fedezet"] = adatok.apply(
    lambda sor: fedezet_szamitas(
        sor["eladasi_ar"],
        sor["termek_kozvetlen_koltsege"],
        sor["platform_dij"]
    ),
    axis=1
)
adatok["platform_dij"] = adatok["eladasi_ar"].apply(
    lambda ar: platform_dij_szamitas(
        ar,
        platform_jutalek,
        platform_minimum_dij,
        afa_kulcs
    )
)

print("\nKalkuláció eredménye:")

print(f"Termék: {adatok['termek'].iloc[0]}")
print(f"Selejt: {adatok['selejt'].iloc[0]:g} db")
print(f"Felhasznált alapanyag: {adatok['felhasznalt_alapanyag'].iloc[0]:g} g")
print(f"Alapanyag ára: {adatok['anyag_ar'].iloc[0]:g} Ft/kg")
print(f"Nyomtatási idő: {adatok['nyomtatasi_ido'].iloc[0]:g} perc")
print(f"Felhasznált energia: {adatok['felhasznalt_energia'].iloc[0]:g} kWh")

print(f"Anyagköltség: {adatok['anyagkoltseg'].iloc[0]:.2f} Ft")
print(f"Energiaköltség: {adatok['energiakoltseg'].iloc[0]:.2f} Ft")
print(f"Közvetlen költség: {adatok['termek_kozvetlen_koltsege'].iloc[0]:.2f} Ft")
print(f"Eladási ár: {adatok['eladasi_ar'].iloc[0]:g} Ft")
print(f"Platformdíj: {adatok['platform_dij'].iloc[0]:.2f} Ft")
print(f"Fedezet: {adatok['fedezet'].iloc[0]:.2f} Ft")