import math

import pandas as pd

from adatkezeles import (
    excel_adatok_beolvasasa,
    beallitasok_szotarba,
    szakdolgozati_minta,
)
from termek_elemzes import termek_koltsegei, platform_arany

def termek_h3_eredmenye(sor, p, eladasi_ar=None):

    k = termek_koltsegei(sor, p, selejttel=False)

    selejt = p["selejtarany"] / 100
    gyartasi = (k["anyag"] + k["energia"] + k["munkadij"]) / (1 - selejt)
    munkadij = k["munkadij"] / (1 - selejt)
    osszes = gyartasi + k["csomagolas"] + k["futar"]

    if eladasi_ar is None:
        eladasi_ar = sor["eladasi_ar"]

    bevetel = eladasi_ar + sor["szallitasi_dij"]
    platformdij = bevetel * platform_arany(p)

    gazdasagi_eredmeny = bevetel - platformdij - osszes
    penzugyi_fedezet = gazdasagi_eredmeny + munkadij

    hipa_levonhato = (
        (k["anyag"] + k["energia"]) / (1 - selejt)
        + k["csomagolas"]
    )

    return {
        "eladasi_ar": eladasi_ar,
        "bevetel": bevetel,
        "hipa_levonhato": hipa_levonhato,
        "platformdij": platformdij,
        "gazdasagi_eredmeny": gazdasagi_eredmeny,
        "penzugyi_fedezet": penzugyi_fedezet,
    }

def piaci_ar(sor):
    if "piaci_ar" in sor and pd.notna(sor["piaci_ar"]):
        return sor["piaci_ar"]
    return sor["eladasi_ar"]

def piaci_arelony(sor, ar=None):
    alternativa = sor["alternativa_beszerzesi_ar"]
    if pd.isna(alternativa):
        return "nincs összehasonlítható adat"
    if ar is None:
        ar = piaci_ar(sor)
    vegosszeg = ar + sor["szallitasi_dij"]
    return "igen" if vegosszeg <= 0.9 * alternativa else "nem"

def havi_eredmenyek(adatok, p, havi_db, piaci=False):
    gazdasagi = 0
    penzugyi = 0
    bevetel = 0
    hipa_levonhato = 0
    for _, sor in adatok.iterrows():
        ar = piaci_ar(sor) if piaci else None
        e = termek_h3_eredmenye(sor, p, eladasi_ar=ar)
        gazdasagi += e["gazdasagi_eredmeny"] * havi_db
        penzugyi += e["penzugyi_fedezet"] * havi_db
        bevetel += e["bevetel"] * havi_db
        hipa_levonhato += e["hipa_levonhato"] * havi_db

    terhek = eves_kozterhek(bevetel * 12, hipa_levonhato * 12, p)
    havi_teher = terhek["osszesen"] / 12 + p["havi_fix_koltseg"]
    gazdasagi -= havi_teher
    penzugyi -= havi_teher
    return gazdasagi, penzugyi

def eves_kozterhek(eves_bevetel, eves_hipa_levonhato, p):
    if p["foallasu"] == 1:
        raise NotImplementedError(
            "A főállású változat (minimális járulékalapok) nincs kidolgozva."
        )

    jovedelem = eves_bevetel * (1 - p["atalanyado_koltseghanyad"] / 100)
    adokoteles = max(0, jovedelem - p["atalanyado_adomentes_jovedelem"])
    szja = adokoteles * p["szja_kulcs"] / 100
    tb = adokoteles * p["tb_jarulek_kulcs"] / 100
    szocho = adokoteles * p["szocho_kulcs"] / 100

    hipa_alap = max(0, eves_bevetel - eves_hipa_levonhato)
    if hipa_alap <= p["hipa_mentessegi_hatar"]:
        hipa = 0
    else:
        hipa = hipa_alap * p["hipa_adomertek"] / 100

    kamara = p["kamarai_hozzajarulas"]

    return {
        "jovedelem": jovedelem,
        "szja": szja,
        "tb": tb,
        "szocho": szocho,
        "hipa_alap": hipa_alap,
        "hipa": hipa,
        "kamara": kamara,
        "osszesen": szja + tb + szocho + hipa + kamara,
        "afa_hatar_felett": eves_bevetel > p["alanyi_afa_ertekhatar"],
    }

def megterulesi_honap(beruhazas, havi_osszeg):
    if havi_osszeg <= 0:
        return None
    return math.ceil(beruhazas / havi_osszeg)


def beruhazasok(p, adatok=None):
    penzugyi = (
        p["indulo_beruhazas"]
        + p["egyeb_indulo_kiadas"]
    )

    gazdasagi = (
        penzugyi
        + p["tervezesi_ido_ora"] * p["kalkulalt_oradij"]
    )

    if adatok is not None:
        for _, sor in adatok.iterrows():
            selejt_anyag = (
                sor["selejt_alapanyag"] / 1000
                * sor["anyag_ar"]
            )
            selejt_energia = (
                sor["selejt_energia"]
                * p["villamos_energia_ar"]
            )
            selejt_munkadij = (
                sor["selejt_kezelesi_ido"] / 60
                * p["kalkulalt_oradij"]
            )
            penzugyi += selejt_anyag + selejt_energia
            gazdasagi += (
                selejt_anyag
                + selejt_energia
                + selejt_munkadij
            )
    return penzugyi, gazdasagi

if __name__ == "__main__":

    adatok, beallitasok = excel_adatok_beolvasasa()
    adatok = szakdolgozati_minta(adatok)
    p = beallitasok_szotarba(beallitasok)

    print(f"\nH3 – TERMÉKENKÉNTI EREDMÉNYEK (selejtarány: {p['selejtarany']:.0f}%)\n")

    for _, sor in adatok.iterrows():
        e = termek_h3_eredmenye(sor, p)

        print(sor["termek"])
        print(f"  Eladási ár:          {e['eladasi_ar']:8.0f} Ft")
        print(f"  Platformdíj:         {e['platformdij']:8.0f} Ft")
        print(f"  Gazdasági eredmény:  {e['gazdasagi_eredmeny']:8.0f} Ft/db")
        print(f"  Pénzügyi fedezet:    {e['penzugyi_fedezet']:8.0f} Ft/db")
        print()

    penzugyi_beruhazas, gazdasagi_beruhazas = beruhazasok(p, adatok)

    print("H3 – MEGTÉRÜLÉS (közterhekkel)\n")
    print(f"  Pénzügyi beruházás:  {penzugyi_beruhazas:8.0f} Ft")
    print(f"  Gazdasági beruházás: {gazdasagi_beruhazas:8.0f} Ft\n")

    for havi_db in [1, 3, 6]:
        gazd, penz = havi_eredmenyek(adatok, p, havi_db)
        h_penz = megterulesi_honap(penzugyi_beruhazas, penz)
        h_gazd = megterulesi_honap(gazdasagi_beruhazas, gazd)

        print(f"Termékenként havi {havi_db} db (összesen {havi_db * len(adatok)} db/hó):")
        for nev, osszeg, honap in [
            ("Pénzügyi", penz, h_penz),
            ("Gazdasági", gazd, h_gazd),
        ]:
            if honap is None:
                print(f"  {nev}: {osszeg:8.0f} Ft/hó, nem térül meg")
            else:
                igen = "igen" if honap <= 24 else "nem"
                print(f"  {nev}: {osszeg:8.0f} Ft/hó, {honap} hónap, 24 hónapon belül: {igen}")
        print()

    print("H3 – SELEJTARÁNY ÉRZÉKENYSÉGVIZSGÁLATA\n")

    for selejtarany in [0, 5, 10]:
        p_valtozat = p.copy()
        p_valtozat["selejtarany"] = selejtarany
        print(f"Selejtarány: {selejtarany}%")

        for havi_db in [1, 3, 6]:
            gazd, penz = havi_eredmenyek(adatok, p_valtozat, havi_db)
            penz_honap = megterulesi_honap(penzugyi_beruhazas, penz)
            gazd_honap = megterulesi_honap(gazdasagi_beruhazas, gazd)
            print(
                f"  {havi_db * len(adatok):2d} db/hó | "
                f"Pénzügyi: {penz_honap} hónap | "
                f"Gazdasági: {gazd_honap} hónap"
            )
        print()

    print("H3 – PIACI ÁRKÉPZÉSI FORGATÓKÖNYV\n")

    for _, sor in adatok.iterrows():
        ar = piaci_ar(sor)
        e = termek_h3_eredmenye(sor, p, eladasi_ar=ar)
        print(
            f"  {sor['termek']}: {ar:.0f} Ft | "
            f"gazdasági eredmény: {e['gazdasagi_eredmeny']:.0f} Ft/db | "
            f"pénzügyi fedezet: {e['penzugyi_fedezet']:.0f} Ft/db | "
            f"10%-os árelőny: {piaci_arelony(sor, ar)}"
        )
    print()

    for havi_db in [1, 3, 6]:
        gazd, penz = havi_eredmenyek(adatok, p, havi_db, piaci=True)
        penz_honap = megterulesi_honap(penzugyi_beruhazas, penz)
        gazd_honap = megterulesi_honap(gazdasagi_beruhazas, gazd)
        print(
            f"  {havi_db * len(adatok):2d} db/hó | "
            f"Pénzügyi: {penz_honap} hónap | "
            f"Gazdasági: {gazd_honap} hónap"
        )
    print()

    print("H3 – ÉVES KÖZTERHEK (költségalapú árazás)\n")

    for havi_db in [1, 3, 6]:
        bev = 0
        lev = 0
        for _, sor in adatok.iterrows():
            e = termek_h3_eredmenye(sor, p)
            bev += e["bevetel"] * havi_db * 12
            lev += e["hipa_levonhato"] * havi_db * 12
        t = eves_kozterhek(bev, lev, p)
        print(f"  {havi_db * len(adatok):2d} db/hó | bevétel: {bev:9.0f} Ft/év")
        print(f"          átalányjövedelem: {t['jovedelem']:9.0f} Ft | "
              f"SZJA: {t['szja']:.0f} | TB: {t['tb']:.0f} | szocho: {t['szocho']:.0f}")
        print(f"          HIPA-alap: {t['hipa_alap']:9.0f} Ft | HIPA: {t['hipa']:.0f} | "
              f"kamara: {t['kamara']:.0f} | összesen: {t['osszesen']:.0f} Ft/év")
        if t["afa_hatar_felett"]:
            print("          FIGYELEM: a bevétel meghaladja az alanyi áfamentességi határt!")
    print()