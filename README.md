# koltseg_kalkulator
3D nyomtatási költségkalkulátor 

A kalkulátor a szakdolgozat gyakorlati részéhez készült.
A célja, hogy a megadott adatok alapján kiszámolja a 3D nyomtatott termék várható előállítási költségét, az egy termékre jutó becsült hasznot, a haszonhányadot, valamint a megadott termékmennyiséghez tartozó összesített költségeket és eredményeket.

Jelenlegi funkciói:
- anyagköltség kiszámítása
- energiafogyasztás becslése, ha nincsen mért adat
- energiaköltség kiszámítása
- a gyártási selejt figyelembevétele
- gyártandó / értékesítendő termékmennyiség kezelése
- referencia gyártási tételben nyomtatott összes darabszám megadása
- csomagolási költség számítása
- kiszámolja az értékesítési platform díját, ehhez figyelembe veszi a szállítási díjat is
- kiszámolja a közvetlen költségeket
- kiszámolja a becsült adózás előtti nyereséget
- kiszámolja a haszonhányad százalékos értékét

A termékekhez tartozó adatokat a Streamlit felületén lehet megadni.
Az általános beállításokat, például a villamos energia árát és a platform díjait a program az adatok/termekadatok.xlsx fájlból olvassa be.

Ha mért energiafogyasztás nem áll rendelkezésre, a program a megadott nyomtatási idő és a nyomtató becsült teljesítményfelvétele alapján becsüli meg az energiafelhasználást.

A selejtes nyomtatások költsége úgy vehető figyelembe, hogy a felhasználó az összes ténylegesen felhasznált alapanyag-, idő- és energiaértéket adja meg, beleértve a sikertelen és szükség esetén a pótló nyomtatások ráfordításait is.

A kalkulátor felhasználói felülete Streamlit-tal 
készült.

A kalkulátor online elérhetősége:

https://3d-nyomtatas-koltsegkalkulator.streamlit.app

Helyi indítás:
```bash
python -m streamlit run felulet.py
```