# koltseg_kalkulator
3D nyomtatási költségkalkulátor 

A kalkulátor a szakdolgozat gyakorlati részéhez készült.
A célja, hogy a megadott adatok alapján kiszámolja a 3D nyomtatott termék várható előállítási költségét, az egy termékre jutó becsült hasznot, a haszonhányadot, valamint a megadott termékmennyiséghez tartozó összesített költségeket és eredményeket. Emellett a szakdolgozatban vizsgált alkatrészeket összeveti a kereskedelmi alternatívákkal, és kiszámolja egy erre épülő kisvállalkozás megtérülését.

A felület három fülből áll:
 - Egyedi kalkuláció: egy tetszőleges termék költségeinek és eredményeinek kiszámítása a felületen megadott adatok alapján.
 - Vizsgált alkatrészek (H1-H2): a szakdolgozatban vizsgált alkatrészek költségei és összevetésük a kereskedelmi alternatívákkal
- Vállalkozás és megtérülés (H3): a vállalkozás havi eredménye, éves közterhei és megtérülési ideje, állítható árképzéssel, havi darabszámmal és selejtaránnyal.

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
- összeveti a vizsgált alkatrészek költségét a kereskedelmi alternatívák árával
- kiszámolja a vállalkozás havi eredményét, éves közterheit, valamint a pénzügyi és gazdasági megtérülési időt

Az egyedi kalkulációhoz a termékekhez tartozó adatokat a Streamlit felületén lehet megadni. A vizsgált alkatrészek adatait és az általános beállításokat, például egyebek között a villamos energia árát, a platform díjait és az adózási paramétereket a program az adatok/termekadatok.xlsx fájlból olvassa be. Új termék az Adatok munkalapon egy új sorba vehető fel, a közös értékek pedig a Beallitasok munkalapon módosíthatók a kód átírása nélkül.

Ha mért energiafogyasztás nem áll rendelkezésre, a program a megadott nyomtatási idő és a nyomtató becsült teljesítményfelvétele alapján becsüli meg az energiafelhasználást. (Kizárólag a dolgozathoz használt Artillery SW X4 Plus nyomtató adataihoz igazodik)

A selejtes nyomtatások költségét a program a referencia gyártási tétel alapján veszi figyelembe: a felhasználó megadja a tételben nyomtatott összes darabot és ebből a selejtes darabok számát, a program pedig a teljes ráfordítást a sikeresen elkészült darabok között osztja fel. A vállalkozási számításban a későbbi gyártás selejtaránya külön, a felületen állítható.

A program fájljai:
- felulet.py - a felhasználói felület
- kalkulacio.py - az egyedi számítások
- adatkezeles.py - adatok beolvasása az Excelből
- termek_elemzes.py - a vizsgált alkatrészek költségei a H1-H2 hipotézisekhez
- megterules.py - a H3 hipotézishez tartozó vállalkozási eredmény és megtérülés számításai
- anyagar_teszt.py - a plusz 20%-os anyagár-változás hatásának ellenőrzése

A kalkulátor felhasználói felülete Streamlit-tel készült.

A kalkulátor online elérhetősége:

https://3d-nyomtatas-koltsegkalkulator.streamlit.app

Helyi indítás:
```bash
python -m streamlit run felulet.py
```