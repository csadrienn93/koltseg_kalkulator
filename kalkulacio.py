from adatkezeles import excel_adatok_beolvasasa


def anyagkoltseg_szamitas(felhasznalt_alapanyag, anyag_ar):
    anyagkoltseg = felhasznalt_alapanyag / 1000 * anyag_ar
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

def energiakoltseg_szamitas(energiafogyasztas, aram_ar):
    energiakoltseg = energiafogyasztas * aram_ar
    return energiakoltseg

def kozvetlen_koltseg_szamitas(anyagkoltseg, energiakoltseg, csomagolasi_koltseg):
    kozvetlen_koltseg = anyagkoltseg + energiakoltseg + csomagolasi_koltseg
    return kozvetlen_koltseg

def fedezet_szamitas(eladasi_ar, termek_kozvetlen_koltsege):
    fedezet = eladasi_ar - termek_kozvetlen_koltsege
    return fedezet

def platform_dij_szamitas(eladasi_ar, jutalek_szazalek, minimum_dij, afa_kulcs):
    jutalek = eladasi_ar * jutalek_szazalek / 100
    if jutalek < minimum_dij:
        jutalek = minimum_dij
    platform_dij = jutalek * (1 + afa_kulcs / 100)
    return platform_dij

def fedezet_szamitas(eladasi_ar, termek_kozvetlen_koltsege, platform_dij):
    fedezet = eladasi_ar - termek_kozvetlen_koltsege - platform_dij
    return fedezet


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

    print("Áram ára:", aram_ar, "Ft/kWh")
    print("Nyomtató fogyasztása:", nyomtato_fogyasztas, "W")

    adatok["anyagkoltseg"] = adatok.apply(
    lambda sor: anyagkoltseg_szamitas(
        sor["felhasznalt_alapanyag"],
        sor["anyag_ar"]
    ),
    axis=1
)
adatok["becsult_energiafogyasztas"] = adatok["nyomtatasi_ido"].apply(
    lambda ido: energiafogyasztas_becslese(
        ido,
        nyomtato_fogyasztas
    )
)
adatok["energiakoltseg"] = adatok["becsult_energiafogyasztas"].apply(
    lambda fogyasztas: energiakoltseg_szamitas(
        fogyasztas,
        aram_ar
    )
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

print(adatok[[
    "termek",
    "felhasznalt_alapanyag",
    "anyag_ar",
    "anyagkoltseg",
    "nyomtatasi_ido",
    "becsult_energiafogyasztas",
    "energiakoltseg",
    "termek_kozvetlen_koltsege",
    "fedezet",
    "eladasi_ar",
    "platform_dij"
]])