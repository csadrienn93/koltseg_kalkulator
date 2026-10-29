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
    # megteruleshez_szukseges_darabszam
)

st.set_page_config(
    page_title="3D nyomtatási költségkalkulátor",
    page_icon="🧮",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("3D nyomtatási költségkalkulátor")

st.write(
    "A kalkulátor egy 3D nyomtatott termék költségeinek "
    "kiszámítására szolgál."
)

termek_oszlop, gyartas_oszlop, ertekesites_oszlop = st.columns(3)

with termek_oszlop:
    st.markdown("### Termék és mennyiség")
    termek = st.text_input("Termék neve")

    darabszam = st.number_input(
        "Gyártandó / értékesítendő mennyiség (db)",
        min_value=1,
        value=1,
        step=1
    )

    rendelesek_szama = st.number_input(
        "Rendelések száma",
        min_value=1,
        max_value=darabszam,
        value=1,
        step=1,
        help=("Add meg, hány külön rendelésben kerül értékesítésre a megadott termékmennyiség. Ha például 12 darab egy vevőhöz kerül, az érték 1.")
    )
    osszes_nyomtatott_darab = st.number_input(
        "Referencia gyártási tételben nyomtatott összes darab",
        min_value=1,
        value=1,
        step=1,
        help="Add meg, összesen hány darab készült el, a selejtes darabokat is beleértve."
    )
    selejt_darabszam = st.number_input(
        "Ebből selejt (db)",
        min_value=0,
        max_value=osszes_nyomtatott_darab - 1,
        value=0,
        step=1
    )

    ertekesitheto_darabszam = osszes_nyomtatott_darab - selejt_darabszam

    st.caption(
        f"Értékesíthető darabszám a referencia gyártási tételben: "
        f"**{ertekesitheto_darabszam} db**"
    )
with gyartas_oszlop:
    st.markdown("### Gyártási adatok")

    anyag_ar = st.number_input(
        "Alapanyag ára (Ft/kg)",
        min_value=0,
        step=100
    )
    felhasznalt_alapanyag = st.number_input("Felhasznált alapanyag a referencia gyártási tételhez (g, selejttel együtt)",
        min_value=0,
        step=1,
        help=("Add meg a referencia gyártási tételhez összesen felhasznált alapanyag mennyiségét, beleértve a selejtes és pótló nyomtatások anyagigényét is.")
    )
    nyomtatasi_ido = st.number_input("Összes nyomtatási idő a referencia gyártási tételhez (perc, selejttel együtt)",
        min_value=0,
        step=1
    )
    energiafogyasztas = st.number_input(
           "Mért energiafogyasztás a referencia gyártási tételhez (kWh, selejttel együtt)",
            min_value=0.0,
            step=0.01,
            format="%.3f",
            help="Add meg a gyártási tételhez összesen felhasznált mért energiát, beleértve a selejtes és pótló nyomtatásokat is. Ha nincs mért adat, hagyd 0 értéken."
        )
with ertekesites_oszlop:
    st.markdown("### Értékesítés")

    csomagolasi_koltseg = st.number_input(
        "Csomagolási költség rendelésenként (Ft)",
        min_value=0,
        step=100
    )
    eladasi_ar = st.number_input(
        "Eladási ár 1 db-ra (Ft)",
        min_value=0,
        step=100
    )
    szallitasi_dij = st.number_input(
        "Vevő által fizetett szállítási díj rendelésenként (Ft)",
        min_value=0,
        step=100
    )
           
if st.button("Számítás"):

        hianyzo_mezok = []

        if not termek:
            hianyzo_mezok.append("Termék neve")

        if anyag_ar <= 0:
            hianyzo_mezok.append("Alapanyag ára")

        if felhasznalt_alapanyag <= 0:
            hianyzo_mezok.append("Felhasznált alapanyag")

        if nyomtatasi_ido <= 0:
            hianyzo_mezok.append("Nyomtatási idő")

        if eladasi_ar <= 0:
            hianyzo_mezok.append("Eladási ár")
          
        if hianyzo_mezok:
            st.warning("A következő kötelező mezőket töltsd ki: "+ ", ".join(hianyzo_mezok))
            st.stop()

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
        #indulo_beruhazas = beallitas_keresese(
        #    beallitasok,
        #    "indulo_beruhazas"
        #)
        # Egy darabra jutó értékek meghatározása

        alapanyag_db = felhasznalt_alapanyag / ertekesitheto_darabszam

        energia_tetel = energiafogyasztas_meghatarozasa(
            energiafogyasztas,
            nyomtatasi_ido,
            nyomtato_fogyasztas
        )

        energia_db = energia_tetel / ertekesitheto_darabszam

        csomagolasi_koltseg_db = (
            csomagolasi_koltseg * rendelesek_szama / darabszam
        )

        szallitasi_dij_db = (
            szallitasi_dij * rendelesek_szama / darabszam
        )

        anyagkoltseg = anyagkoltseg_szamitas(
            alapanyag_db,
            anyag_ar
        )

        felhasznalt_energia = energia_db
        
        energiakoltseg = energiakoltseg_szamitas(
            felhasznalt_energia,
            aram_ar
        )   
        kozvetlen_koltseg = kozvetlen_koltseg_szamitas(
            anyagkoltseg,
            energiakoltseg,
            csomagolasi_koltseg_db
        )
        platform_dij = platform_dij_szamitas(
            eladasi_ar,
            szallitasi_dij_db,
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
        #megterules_darabszam = megteruleshez_szukseges_darabszam(
        #    indulo_beruhazas,
        #    becsult_eredmeny
        #)
        osszes_alapanyag = alapanyag_db * darabszam
        osszes_energia = felhasznalt_energia * darabszam

        osszes_anyagkoltseg = anyagkoltseg * darabszam
        osszes_energiakoltseg = energiakoltseg * darabszam
        osszes_csomagolasi_koltseg = csomagolasi_koltseg * rendelesek_szama
        osszes_kozvetlen_koltseg = kozvetlen_koltseg * darabszam

        osszes_szallitasi_dij = szallitasi_dij * rendelesek_szama
        osszes_platform_dij = platform_dij * darabszam
        osszes_arbevetel = eladasi_ar * darabszam
        osszes_becsult_eredmeny = becsult_eredmeny * darabszam
    
        st.divider()

        eredmeny_bal, eredmeny_jobb = st.columns(2, border=True)

        with eredmeny_bal:
            st.subheader("Költség és eredmény – 1 db-ra")

            if energiafogyasztas > 0:
             st.caption(
                    "Az energiaköltség mért energiafogyasztás alapján készült."
                )
            else:
                st.caption(
                    "Az energiaköltség becsült energiafogyasztás alapján készült."
                )

            bal1, bal2 = st.columns(2)

            with bal1:
                st.metric("Anyagköltség", f"{anyagkoltseg:.0f} Ft")
                st.metric(
                    "Közvetlen költség",
                    f"{kozvetlen_koltseg:.0f} Ft"
                )
                st.metric(
                    "Energiafelhasználás / db",
                    f"{felhasznalt_energia:.2f} kWh"
                )
                st.metric(
                "Haszonhányad",
                 f"{haszonhanyad:.2f} %"
                )

            with bal2:
                st.metric(
                    "Energiaköltség",
                    f"{energiakoltseg:.0f} Ft"
                )
                st.metric(
                    "Platformdíj",
                    f"{platform_dij:.0f} Ft"
                )
                st.metric(
                    "Becsült eredmény / db",
                    f"{becsult_eredmeny:.0f} Ft"
                )


        with eredmeny_jobb:
            st.subheader(
                f"Összesítés – {darabszam} db, {rendelesek_szama} rendelés"
            )

            jobb1, jobb2 = st.columns(2)

            with jobb1:
                st.metric(
                    "Összes anyagköltség",
                    f"{osszes_anyagkoltseg:.0f} Ft"
                )
                st.metric(
                    "Összes csomagolási költség",
                    f"{osszes_csomagolasi_koltseg:.0f} Ft"
                )
                st.metric(
                    "Összes platformdíj",
                    f"{osszes_platform_dij:.0f} Ft"
                )
                st.metric(
                    "Becsült összes eredmény",
                    f"{osszes_becsult_eredmeny:.0f} Ft"
                )

            with jobb2:
                st.metric(
                    "Összes energiaköltség",
                    f"{osszes_energiakoltseg:.0f} Ft"
                )
                st.metric(
                    "Összes közvetlen költség",
                    f"{osszes_kozvetlen_koltseg:.0f} Ft"
                )
                st.metric(
                    "Termékek eladási ára",
                    f"{osszes_arbevetel:.0f} Ft"
                )

            st.caption(
                f"Összes felhasznált alapanyag: {osszes_alapanyag:.0f} g | "
                f"Összes energiafelhasználás: {osszes_energia:.2f} kWh | "
                f"Összes szállítási díj: {osszes_szallitasi_dij:.0f} Ft"
                )

      

       # st.divider()
        #st.subheader("Beruházás megtérülése")

       # megterules1, megterules2 = st.columns(2)

       # with megterules1:
        #    st.metric(
        #        "Induló beruházás",
         #       f"{indulo_beruhazas:.0f} Ft"
          #  )
        #with megterules2:
         #   if megterules_darabszam is not None:
          #      st.metric(
           #         "Megtérüléshez szükséges eladás",
            #        f"{megterules_darabszam} db"
             #   )
            #else:
             #   st.warning("A jelenlegi eredmény mellett a beruházás megtérülése nem számítható.")