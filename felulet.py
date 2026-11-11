import pandas as pd
import streamlit as st

from adatkezeles import (
    excel_adatok_beolvasasa,
    beallitasok_szotarba,
    szakdolgozati_minta,
)
from kalkulacio import (
    anyagkoltseg_szamitas,
    beallitas_keresese,
    energiafogyasztas_meghatarozasa,
    energiakoltseg_szamitas,
    kozvetlen_koltseg_szamitas,
    platform_dij_szamitas,
    becsult_eredmeny_szamitas,
    kalkulalt_munkadij_szamitas,
)
from termek_elemzes import (
    termek_koltsegei,
    onkoltsegi_vegosszeg,
    minimalis_eladasi_ar,
)
from megterules import (
    piaci_ar,
    piaci_arelony,
    termek_h3_eredmenye,
    havi_eredmenyek,
    eves_kozterhek,
    megterulesi_honap,
    beruhazasok,
)


def ft(ertek):
    return f"{ertek:,.0f} Ft".replace(",", " ")


def termekek_kivalasztasa(kulcs):
    adatok, beallitasok = excel_adatok_beolvasasa()
    minden = st.checkbox(
        "Minden termék bevonása",
        value=False,
        key=kulcs,
        help=(
            "Kikapcsolva csak a szakdolgozat rögzített mintája (szakdolgozat = 1) "
            "szerepel. Bekapcsolva az Excelben szereplő összes termék."
        ),
    )
    if not minden:
        adatok = szakdolgozati_minta(adatok)
    st.caption(
        f"Bevont termékek: {len(adatok)} "
        f"({'összes rögzített termék' if minden else 'szakdolgozati minta'})"
    )
    if minden and len(adatok) != len(szakdolgozati_minta(adatok)):
        st.warning(
            "A szakdolgozati mintán kívüli termékek is szerepelnek, ezért az "
            "eredmények eltérnek a szakdolgozat H1–H3 eredményeitől."
        )
    return adatok, beallitasok_szotarba(beallitasok)

def egyedi_kalkulacio():
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
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
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
        kezelesi_ido_perc = st.number_input(
                "Összes aktív kezelési idő a referencia gyártási tételhez (perc)",
                min_value=0,
                value=0,
                step=1,
                help=("A teljes referencia gyártási tétel aktív munkaideje: nyomtatás előkészítése, indítása, alkatrészek levétele, utómunka és ellenőrzés." 
            "Több nyomtatási ciklus esetén az összes kezelési időt add meg. A felügyelet nélküli nyomtatási időt és az egyszeri CAD-tervezést ne számold bele.")
        )
        oradij = st.number_input(
            "Kalkulált munkadíj (Ft/óra)",
            min_value=0,
            value=3000,
            step=500
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

    if not st.button("Számítás"):
        return

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
        return

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
    futarkoltseg = beallitas_keresese(
        beallitasok,
        "atlagos_futarkoltseg"
    )

    alapanyag_db = felhasznalt_alapanyag / ertekesitheto_darabszam

    munkadij_tetel = kalkulalt_munkadij_szamitas(
        kezelesi_ido_perc,
        oradij
    )

    munkadij_db = munkadij_tetel / ertekesitheto_darabszam

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
    futarkoltseg_db = (
        futarkoltseg * rendelesek_szama / darabszam
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
    teljes_gazdasagi_koltseg = (
        kozvetlen_koltseg + platform_dij + munkadij_db
    )
    gazdasagi_eredmeny = (
        eladasi_ar + szallitasi_dij_db - teljes_gazdasagi_koltseg - futarkoltseg_db
    )
    becsult_eredmeny = becsult_eredmeny_szamitas(
        eladasi_ar,
        kozvetlen_koltseg,
        platform_dij
    )
    becsult_eredmeny += szallitasi_dij_db - futarkoltseg_db

    gazdasagi_eredmenyhanyad = (
        gazdasagi_eredmeny / (eladasi_ar + szallitasi_dij_db) * 100
    )

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
    osszes_munkadij = munkadij_db * darabszam
    osszes_gazdasagi_eredmeny = gazdasagi_eredmeny * darabszam

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
                "Gazdasági eredményhányad",
                f"{gazdasagi_eredmenyhanyad:.2f} %"
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

            st.metric(
                "Kalkulált munkadíj / db",
                f"{munkadij_db:.0f} Ft"
            )
            st.metric(
                "Gazdasági eredmény / db",
                f"{gazdasagi_eredmeny:.0f} Ft"
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
            st.metric(
                "Összes kalkulált munkadíj",
                f"{osszes_munkadij:.0f} Ft"
            )
            st.metric(
                "Összes gazdasági eredmény",
                f"{osszes_gazdasagi_eredmeny:.0f} Ft"
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
            f"Összes felhasznált alapanyag: {osszes_alapanyag:.2f} g | "
            f"Összes energiafelhasználás: {osszes_energia:.2f} kWh | "
            f"Összes szállítási díj: {osszes_szallitasi_dij:.0f} Ft"
            )

    st.caption("Egy termékre vonatkozó, adózás előtti számítás. A saját kalkulált munkadíj nem pénzkiadásként szerepel.")

def vizsgalt_alkatreszek():
    adatok, p = termekek_kivalasztasa("minden_termek_h1h2")

    st.write(
        "Az öt vizsgált alkatrész teljes költsége a dokumentált próbanyomtatási selejttel együtt, valamint a H1 és a H2 hipotézis termékenkénti eredménye."
        "Az adatok az Excel *Adatok* és *Beallitasok* munkalapjáról származnak."
    )

    st.caption(
        "A költségek a dokumentált próbanyomtatási selejtet is tartalmazzák, így az első gyártási kör költségeit mutatják. "
    "A H3 vállalkozási modellben ez a selejt egyszeri induló ráfordításként szerepel."
    )
    sorok = []
    h1_db = 0
    h2_db = 0
    for _, sor in adatok.iterrows():
        k = termek_koltsegei(sor, p, selejttel=True)
        vegosszeg = onkoltsegi_vegosszeg(k, p)
        alternativa = sor["alternativa_beszerzesi_ar"]

        h1 = k["munkadij"] > k["anyag"] + k["energia"]
        h1_db += h1

        if pd.notna(alternativa):
            h2 = vegosszeg < alternativa
            h2_db += h2
            h2_szoveg = "igen" if h2 else "nem"
            alternativa_szoveg = ft(alternativa)
        else:
            h2_szoveg = "nincs összehasonlítható adat"
            alternativa_szoveg = "–"

        sorok.append({
            "Alkatrész": sor["termek"],
            "Anyag": ft(k["anyag"]),
            "Energia": ft(k["energia"]),
            "Munkadíj": ft(k["munkadij"]),
            "Csomagolás": ft(k["csomagolas"]),
            "Futár": ft(k["futar"]),
            "Teljes költség": ft(k["osszes"]),
            "Önköltségi végösszeg": ft(vegosszeg),
            "Minimális ár": ft(minimalis_eladasi_ar(k, sor, p)),
            "Alternatíva": alternativa_szoveg,
            "H1": "igen" if h1 else "nem",
            "H2": h2_szoveg,
        })

    st.dataframe(pd.DataFrame(sorok), hide_index=True)

    bal, jobb = st.columns(2, border=True)
    with bal:
        st.metric("H1 teljesül", f"{h1_db} / {len(adatok)} terméknél")
        st.caption("H1: a kalkulált munkadíj meghaladja az anyag- és energiaköltséget.")
    with jobb:
        st.metric("H2 teljesül", f"{h2_db} terméknél")
        if st.session_state["minden_termek_h1h2"]:
            st.info(
                "A táblázat az összes terméket tartalmazza. A szakdolgozati "
                "H1–H2 hipotézisek értékelése kizárólag az eredeti kutatási "
                "mintára vonatkozik."
            )
        elif h2_db >= 3:
            st.success(
                "A H2 a szakdolgozati mintában teljesül (legalább három "
                "alkatrésznél olcsóbb a 3D nyomtatott változat)."
            )
        else:
            st.error(
                "A H2 a szakdolgozati mintában nem teljesül (háromnál "
                "kevesebb alkatrésznél olcsóbb a 3D nyomtatott változat)."
            )

    st.caption(
        "Önköltségi végösszeg: az a vevő által fizetendő legkisebb összeg "
        "(termékár és szállítás), amelyből a platformdíj levonása után "
        "minden költség megtérül. A H2 ezt veti össze a kereskedelmi "
        "alternatíva szállítással növelt beszerzési árával."
    )

def vallalkozas_megterules():
    adatok, p = termekek_kivalasztasa("minden_termek_h3")

    st.write(
        "Feltételezett értékesítési forgatókönyv mellett a vállalkozás havi "
        "eredménye, éves közterhei és a beruházás megtérülése. A "
        "forgatókönyvek érzékenységvizsgálatot szolgálnak, nem keresleti "
        "előrejelzések."
    )
    st.caption(
        "A dokumentált próbanyomtatási selejt egyszeri induló ráfordításként szerepel a beruházásban. "
        "A selejtarány csúszka ettől elkülönítve a későbbi gyártás feltételezett selejtarányát veszi figyelembe."
    )
    
    v1, v2, v3 = st.columns(3)
    with v1:
        arazas = st.radio(
            "Árképzés",
            ["Költségalapú (Excel eladási árai)", "Piaci árképzés (10%-os árelőny céljával)"],
        )
    with v2:
        havi_db = st.number_input(
            "Havi értékesítés termékenként (db)", min_value=1, value=3, step=1,
            help="Az alapforgatókönyv termékenként 3 db, összesen 15 db/hó."
        )
    with v3:
        selejtarany = st.slider(
            "Selejtarány (%)", min_value=0, max_value=20,
            value=int(p["selejtarany"]), step=1,
            help="A legyártott darabok selejtes hányada. Érzékenységvizsgálat: 0, 5, 10%."
        )

    piaci = arazas.startswith("Piaci")
    st.info(
        f"Havi értékesítés: {havi_db} db/termék × {len(adatok)} termék = "
        f"összesen {havi_db * len(adatok)} db/hó"
    )
    q = dict(p)
    q["selejtarany"] = selejtarany

    sorok = []
    eves_bevetel = 0
    eves_hipa_levonhato = 0
    for _, sor in adatok.iterrows():
        ar = piaci_ar(sor) if piaci else None
        e = termek_h3_eredmenye(sor, q, eladasi_ar=ar)
        eves_bevetel += e["bevetel"] * havi_db * 12
        eves_hipa_levonhato += e["hipa_levonhato"] * havi_db * 12
        sorkep = {
            "Alkatrész": sor["termek"],
            "Eladási ár": ft(e["eladasi_ar"]),
            "Platformdíj": ft(e["platformdij"]),
            "Gazdasági eredmény / db": ft(e["gazdasagi_eredmeny"]),
            "Pénzügyi fedezet / db": ft(e["penzugyi_fedezet"]),
        }
        if piaci:
            arelony = piaci_arelony(sor, e["eladasi_ar"])
            if "piaci_ar" not in sor or pd.isna(sor["piaci_ar"]):
                arelony = "nincs piaci ár, a költségalapú ár szerepel"
            elif arelony == "nincs összehasonlítható adat":
                arelony = "nincs összehasonlítható adat (feltételezett ár)"
            sorkep["10%-os árelőny"] = arelony
        sorok.append(sorkep)

    st.markdown("#### Termékenkénti eredmény")
    st.dataframe(pd.DataFrame(sorok), hide_index=True)
    if piaci:
        st.caption(
            "Piaci ár: az Excel piaci_ar oszlopa. Ahol a 10%-os árelőny „nem”, "
            "ott a költségeket fedező ár mellett a tervezett árelőny nem "
            "teljesíthető. Összehasonlítható alternatíva hiányában az ár "
            "feltételezett forgatókönyvi ár."
        )

    gazd, penz = havi_eredmenyek(adatok, q, havi_db, piaci=piaci)
    penzugyi_beruhazas, gazdasagi_beruhazas = beruhazasok(p, adatok)
    h_penz = megterulesi_honap(penzugyi_beruhazas, penz)
    h_gazd = megterulesi_honap(gazdasagi_beruhazas, gazd)

    def honap_szoveg(honap):
        return "nem térül meg" if honap is None else f"{honap} hónap"

    st.markdown(f"#### Megtérülés – összesen {havi_db * len(adatok)} db/hó")
    bal, jobb = st.columns(2, border=True)
    with bal:
        st.markdown("**Pénzügyi megtérülés**")
        st.metric("Beruházás", ft(penzugyi_beruhazas))
        st.metric("Havi pénzügyi fedezet (közterhek után)", ft(penz))
        st.metric("Megtérülési idő", honap_szoveg(h_penz))
    with jobb:
        st.markdown("**Gazdasági megtérülés**")
        st.metric("Beruházás (tervezési munkával)", ft(gazdasagi_beruhazas))
        st.metric("Havi gazdasági eredmény (közterhek után)", ft(gazd))
        st.metric("Megtérülési idő", honap_szoveg(h_gazd))

    alapforgatokonyv = (
        not st.session_state["minden_termek_h3"]
        and not piaci
        and havi_db == 3
        and selejtarany == 0
    )
    if alapforgatokonyv:
        if h_gazd is not None and h_gazd <= 24:
            st.success(
                f"A H3 az alapforgatókönyvben teljesül: a gazdasági "
                f"megtérülés {h_gazd} hónap (legfeljebb 24)."
            )
        else:
            st.error(
                f"A H3 az alapforgatókönyvben nem teljesül: a gazdasági "
                f"megtérülés {honap_szoveg(h_gazd)} (több mint 24)."
            )
    else:
        st.info(
            "Ez alternatív forgatókönyv. A H3 hipotézis értékelése a "
            "szakdolgozati minta 15 db/hó, 0% selejt és költségalapú "
            "árazás mellett számított eredményére vonatkozik."
        )

    honapok = range(0, 37)
    halmozott = pd.DataFrame({
        "Pénzügyi (Ft)": [-penzugyi_beruhazas + h * penz for h in honapok],
        "Gazdasági (Ft)": [-gazdasagi_beruhazas + h * gazd for h in honapok],
    }, index=pd.Index(honapok, name="Hónap"))
    st.markdown("#### Halmozott eredmény 36 hónapra")
    st.line_chart(halmozott)
    st.caption("A görbe a nulla vonalat a megtérülés hónapjában éri el.")

    t = eves_kozterhek(eves_bevetel, eves_hipa_levonhato, q)
    st.markdown("#### Éves közterhek")
    st.dataframe(pd.DataFrame([
        {"Tétel": "Éves bevétel", "Összeg": ft(eves_bevetel)},
        {"Tétel": "Átalányban megállapított jövedelem", "Összeg": ft(t["jovedelem"])},
        {"Tétel": "SZJA", "Összeg": ft(t["szja"])},
        {"Tétel": "TB-járulék", "Összeg": ft(t["tb"])},
        {"Tétel": "Szociális hozzájárulási adó", "Összeg": ft(t["szocho"])},
        {"Tétel": "HIPA-alap (általános módszer)", "Összeg": ft(t["hipa_alap"])},
        {"Tétel": "Helyi iparűzési adó", "Összeg": ft(t["hipa"])},
        {"Tétel": "Kamarai hozzájárulás", "Összeg": ft(t["kamara"])},
        {"Tétel": "Közterhek összesen", "Összeg": ft(t["osszesen"])},
    ]), hide_index=True)
    if t["afa_hatar_felett"]:
        st.warning("Az éves bevétel meghaladja az alanyi adómentesség értékhatárát.")
    st.caption(
        "Mellékállású, átalányadózó, alanyi adómentes egyéni vállalkozás. "
        "Az adómentes jövedelemrészig nincs SZJA, TB-járulék és szocho; a "
        "HIPA a helyi mentességi határig 0 Ft."
    )

    st.markdown(f"#### Forgatókönyvek összehasonlítása ({selejtarany}% selejttel)")
    osszevetes = []
    for nev, forgatokonyv_piaci in [("Költségalapú", False), ("Piaci", True)]:
        for db in [1, 3, 6]:
            g, f = havi_eredmenyek(adatok, q, db, piaci=forgatokonyv_piaci)
            osszevetes.append({
                "Árképzés": nev,
                "Értékesítés": f"{db * len(adatok)} db/hó",
                "Pénzügyi megtérülés": honap_szoveg(megterulesi_honap(penzugyi_beruhazas, f)),
                "Gazdasági megtérülés": honap_szoveg(megterulesi_honap(gazdasagi_beruhazas, g)),
            })
    st.dataframe(pd.DataFrame(osszevetes), hide_index=True)

st.set_page_config(
    page_title="3D nyomtatási költségkalkulátor",
    page_icon="🧮",
    layout="wide"
)
st.markdown(
    """
    <style>
    [data-testid="stHeaderActionElements"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("3D nyomtatási költségkalkulátor")

ful_egyedi, ful_termekek, ful_megterules = st.tabs([
    "Egyedi kalkuláció",
    "Vizsgált alkatrészek (H1–H2)",
    "Vállalkozás és megtérülés (H3)",
])

with ful_egyedi:
    egyedi_kalkulacio()
with ful_termekek:
    vizsgalt_alkatreszek()
with ful_megterules:
    vallalkozas_megterules()