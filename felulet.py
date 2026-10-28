import streamlit as st

from adatkezeles import excel_adatok_beolvasasa
from kalkulacio import (
    anyagkoltseg_szamitas,
    beallitas_keresese,
    energiafogyasztas_meghatarozasa,
    energiakoltseg_szamitas,
    kozvetlen_koltseg_szamitas,
    platform_dij_szamitas,
    becsult_eredmeny_szamitas,
    haszonhanyad_szamitas,
    megteruleshez_szukseges_darabszam
)

st.set_page_config(
    page_title="3D nyomtatási költségkalkulátor",
    page_icon="🧮",
    layout="centered"
)

st.title("3D nyomtatási költségkalkulátor")

st.write(
    "A kalkulátor egy 3D nyomtatott termék költségeinek "
    "kiszámítására szolgál."
)

st.subheader("Termék adatai")


bal, jobb = st.columns(2)

with bal:
    termek = st.text_input("Termék neve")

    anyag_ar = st.number_input(
        "Alapanyag ára (Ft/kg)",
        min_value=0,
        step=100
    )
    felhasznalt_alapanyag = st.number_input(
        "Összes felhasznált alapanyag (g, selejttel együtt)",
        min_value=0,
        step=1,
        help="Add meg az értékesíthető darab elkészítéséhez összesen felhasznált alapanyag mennyiségét, beleértve a selejtes nyomtatások anyagigényét is."
)
    nyomtatasi_ido = st.number_input(
        "Összes nyomtatási idő (perc, selejttel együtt)",
        min_value=0,
        step=1
    )
with jobb:
    csomagolasi_koltseg = st.number_input(
        "Csomagolási költség (Ft)",
        min_value=0,
        step=100
    )
    eladasi_ar = st.number_input(
        "Eladási ár (Ft)",
        min_value=0,
        step=100
    )
    szallitasi_dij = st.number_input(
        "Vevő által fizetett szállítási díj (Ft)",
        min_value=0,
        step=100
    )
    energiafogyasztas = st.number_input(
       "Összes mért energiafogyasztás (kWh, selejttel együtt)",
        min_value=0.0,
        step=0.01,
        format="%.3f",
        help="Add meg az értékesíthető darab elkészítéséhez összesen felhasznált mért energiát, beleértve a selejtes nyomtatásokat is. Ha nincs mért adat, hagyd 0 értéken."
    )
    
   
if st.button("Számítás"):

    if not termek:
        st.warning("Add meg a termék nevét.")

    elif (
        anyag_ar <= 0
        or felhasznalt_alapanyag <= 0
        or nyomtatasi_ido <= 0
        or eladasi_ar <= 0
    ):
        st.warning("Töltsd ki a szükséges adatokat.")

    else:
     
        _, beallitasok = excel_adatok_beolvasasa()

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
        indulo_beruhazas = beallitas_keresese(
            beallitasok,
            "indulo_beruhazas"
        )
        anyagkoltseg = anyagkoltseg_szamitas(
            felhasznalt_alapanyag,
            anyag_ar
        )
        felhasznalt_energia = energiafogyasztas_meghatarozasa(
            energiafogyasztas,
            nyomtatasi_ido,
            nyomtato_fogyasztas
        )
        energiakoltseg = energiakoltseg_szamitas(
            felhasznalt_energia,
            aram_ar
        )   
        kozvetlen_koltseg = kozvetlen_koltseg_szamitas(
            anyagkoltseg,
            energiakoltseg,
            csomagolasi_koltseg
        )
        platform_dij = platform_dij_szamitas(
            eladasi_ar,
            szallitasi_dij,
            platform_jutalek,
            platform_helyi_felar
        )
        becsult_eredmeny = becsult_eredmeny_szamitas(
            eladasi_ar,
            kozvetlen_koltseg,
            platform_dij
        )
        haszonhanyad = haszonhanyad_szamitas(
            becsult_eredmeny,
            eladasi_ar
        )
        megterules_darabszam = megteruleshez_szukseges_darabszam(
            indulo_beruhazas,
            becsult_eredmeny
        )
               
        st.divider()
        st.subheader("Kalkuláció eredménye")

        if energiafogyasztas > 0:
            st.caption("Az energiaköltség mért energiafogyasztás alapján készült.")
        else:
            st.caption("Az energiaköltség becsült energiafogyasztás alapján készült.")


        oszlop1, oszlop2, oszlop3 = st.columns(3)

        with oszlop1:
            st.metric("Anyagköltség", f"{anyagkoltseg:.0f} Ft")

        with oszlop2:
            st.metric("Energiaköltség", f"{energiakoltseg:.0f} Ft")

        with oszlop3:
            st.metric("Közvetlen költség", f"{kozvetlen_koltseg:.0f} Ft")


        oszlop4, oszlop5 = st.columns(2)

        with oszlop4:
            st.metric(
                "Összes energiafelhasználás",
                f"{felhasznalt_energia:.2f} kWh"
            )

        with oszlop5:
            st.metric(
                "Platformdíj",
                f"{platform_dij:.0f} Ft"
            )

        st.divider()
        st.subheader("Gazdasági eredmény")

        eredmeny1, eredmeny2 = st.columns(2)

        with eredmeny1:
            st.metric(
                "Becsült haszon / db",
                f"{becsult_eredmeny:.0f} Ft"
            )
        with eredmeny2:
            st.metric(
                "Haszonhányad",
                f"{haszonhanyad:.2f} %"
            )

        st.divider()
        st.subheader("Beruházás megtérülése")

        megterules1, megterules2 = st.columns(2)

        with megterules1:
            st.metric(
                "Induló beruházás",
                f"{indulo_beruhazas:.0f} Ft"
            )
        with megterules2:
            if megterules_darabszam is not None:
                st.metric(
                    "Megtérüléshez szükséges eladás",
                    f"{megterules_darabszam} db"
                )
            else:
                st.warning("A jelenlegi eredmény mellett a beruházás megtérülése nem számítható.")