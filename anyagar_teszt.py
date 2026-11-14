from adatkezeles import excel_adatok_beolvasasa, beallitasok_szotarba, szakdolgozati_minta
from megterules import havi_eredmenyek, beruhazasok, megterulesi_honap

adatok, beallitasok = excel_adatok_beolvasasa()
adatok = szakdolgozati_minta(adatok)
p = beallitasok_szotarba(beallitasok)
p["selejtarany"] = 0

print("Alapanyagárak (Ft/kg):")
for _, sor in adatok.iterrows():
    print(f"  {sor['termek']}: {sor['anyag_ar']:,.0f} -> {sor['anyag_ar'] * 1.2:,.0f}")

penz_beruhazas, gazd_beruhazas = beruhazasok(p, adatok)
print(f"Induló ráfordítás: pénzügyi {penz_beruhazas:,.0f} Ft, gazdasági {gazd_beruhazas:,.0f} Ft")

for szorzo in (1.0, 1.2):
    vizsgalt = adatok.copy()
    vizsgalt["anyag_ar"] = vizsgalt["anyag_ar"] * szorzo
    gazd, penz = havi_eredmenyek(vizsgalt, p, 3)
    print(
        f"Alapanyagár x{szorzo}: "
        f"pénzügyi {penz:,.0f} Ft/hó, {megterulesi_honap(penz_beruhazas, penz)} hónap | "
        f"gazdasági {gazd:,.0f} Ft/hó, {megterulesi_honap(gazd_beruhazas, gazd)} hónap"
    )