import streamlit as st

from adatkezeles import excel_adatok_beolvasasa
from kalkulacio import (
    anyagkoltseg_szamitas,
    beallitas_keresese,
    energiafogyasztas_meghatarozasa,
    energiakoltseg_szamitas,
    kozvetlen_koltseg_szamitas,
    platform_dij_szamitas,
    fedezet_szamitas,
    haszonhanyad_szamitas
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
        "Felhasznált alapanyag (g)",
        min_value=0,
        step=1
    )
    nyomtatasi_ido = st.number_input(
        "Nyomtatási idő (perc)",
        min_value=0,
        step=1
    )
with jobb:
    energiafogyasztas = st.number_input(
        "Energiafogyasztás (kWh) – ha ismert",
        min_value=0.0,
        step=0.01
    )
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
    selejt = st.number_input(
        "Selejtek száma (db)",
        min_value=0,
        step=1
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
        platform_minimum_dij = beallitas_keresese(
            beallitasok,
            "platform_minimum_dij"
        )
        afa_kulcs = beallitas_keresese(
            beallitasok,
            "afa_kulcs"
        )
        anyagkoltseg = anyagkoltseg_szamitas(
            felhasznalt_alapanyag,
            anyag_ar,
            selejt
        )
        felhasznalt_energia = energiafogyasztas_meghatarozasa(
            energiafogyasztas,
            nyomtatasi_ido,
            nyomtato_fogyasztas
        )
        energiakoltseg = energiakoltseg_szamitas(
            felhasznalt_energia,
            aram_ar,
            selejt
        )
        kozvetlen_koltseg = kozvetlen_koltseg_szamitas(
            anyagkoltseg,
            energiakoltseg,
            csomagolasi_koltseg
        )
        platform_dij = platform_dij_szamitas(
            eladasi_ar,
            platform_jutalek,
            platform_minimum_dij,
            afa_kulcs
        )
        fedezet = fedezet_szamitas(
            eladasi_ar,
            kozvetlen_koltseg,
            platform_dij
        )
        haszonhanyad = haszonhanyad_szamitas(
            fedezet,
            eladasi_ar
        )
        
        st.divider()
        st.subheader("Kalkuláció eredménye")

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
                "Felhasznált energia",
                f"{felhasznalt_energia:.2f} kWh"
            )
        with oszlop5:
            st.metric(
                "Meska díj",
                f"{platform_dij:.0f} Ft"
            )

        st.divider()
        st.subheader("Haszon")

        haszon1, haszon2 = st.columns(2)

        with haszon1:
            st.metric(
                "Becsült haszon / db",
                f"{fedezet:.0f} Ft"
            )
        with haszon2:
            st.metric(
                "Haszonhányad",
                f"{haszonhanyad:.2f} %"
            )