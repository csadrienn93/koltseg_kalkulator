# koltseg_kalkulator
3D nyomtatási költség- és megtérülési kalkulátor szakdolgozathoz

A szakdolgozat gyakorlati részéhez készülő Pyton alapú költség kalkulátor.
A kalkulátor célja, hogy a megfelelő költségadatok beolvasása után meghatározza a termék eladásából származó hasznot.

Jelenlegi funkciói:
- anyagköltség kiszámítása
- energia fogyasztás becslése, ha nincsen mért adat
- energia költség kiszámítása
- figyelembe veszi a selejtes nyomtatásokat
- számol a csomagolás költségeivel
- számol az eladási platform költségeivel (jelenleg ez a Meska)
- meghatározza a közvetlen költségeket
- becslést számít a várható haszonra
- kiszámolja a haszonhányad százalékos értékét

A kalkulátor az 'adatok/termékadatok.xlsx' Excel fájlt használja az adatok tárolására.

A kalkulátor felhasználói felülete Streamlit-tal készült.
Indítás:
```bash
python -m streamlit run felulet.py
```