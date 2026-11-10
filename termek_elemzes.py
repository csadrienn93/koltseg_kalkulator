from adatkezeles import excel_adatok_beolvasasa, beallitasok_szotarba


def termek_koltsegei(sor, p, selejttel=False):

    anyag_g = sor["felhasznalt_alapanyag"]
    energia_kwh = sor["energiafogyasztas"]
    kezeles_perc = sor["kezelesi_ido"]

    if selejttel:
        anyag_g += sor["selejt_alapanyag"]
        energia_kwh += sor["selejt_energia"]
        kezeles_perc += sor["selejt_kezelesi_ido"]

    anyag = anyag_g / 1000 * sor["anyag_ar"]
    energia = energia_kwh * p["villamos_energia_ar"]
    munkadij = kezeles_perc / 60 * p["kalkulalt_oradij"]
    csomagolas = sor["csomagolasi_koltseg"]
    futar = p["atlagos_futarkoltseg"]

    return {
        "anyag": anyag,
        "energia": energia,
        "munkadij": munkadij,
        "csomagolas": csomagolas,
        "futar": futar,
        "osszes": anyag + energia + munkadij + csomagolas + futar,
    }


def platform_arany(p):
    return (p["platform_jutalek"] + p["platform_helyi_felar"]) / 100


def onkoltsegi_vegosszeg(koltsegek, p):
    return koltsegek["osszes"] / (1 - platform_arany(p))


def minimalis_eladasi_ar(koltsegek, sor, p):
    return onkoltsegi_vegosszeg(koltsegek, p) - sor["szallitasi_dij"]


if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()
    p = beallitasok_szotarba(beallitasok)

    for _, sor in adatok.iterrows():
        k = termek_koltsegei(sor, p, selejttel=True)

        print("\n" + sor["termek"])
        print(f"  Anyag:        {k['anyag']:8.0f} Ft")
        print(f"  Energia:      {k['energia']:8.0f} Ft")
        print(f"  Munkadíj:     {k['munkadij']:8.0f} Ft")
        print(f"  Csomagolás:   {k['csomagolas']:8.0f} Ft")
        print(f"  Futár:        {k['futar']:8.0f} Ft")
        print(f"  Összesen:     {k['osszes']:8.0f} Ft")

        h1 = k["munkadij"] > k["anyag"] + k["energia"]
        print(f"  H1 (munkadíj > anyag + energia): {'igen' if h1 else 'nem'}")

        vegosszeg = onkoltsegi_vegosszeg(k, p)
        print(f"  Önköltségi végösszeg a vevőnek: {vegosszeg:8.0f} Ft")
        print(f"  Ebből minimális termékár:       {minimalis_eladasi_ar(k, sor, p):8.0f} Ft")

        alternativa = sor["alternativa_beszerzesi_ar"]
        if alternativa == alternativa:
            olcsobb = vegosszeg < alternativa
            print(f"  Kereskedelmi alternatíva:       {alternativa:8.0f} Ft")
            print(f"  H2 (3D nyomtatott olcsóbb): {'igen' if olcsobb else 'nem'}")
        else:
            print("  Kereskedelmi alternatíva: nincs adat")