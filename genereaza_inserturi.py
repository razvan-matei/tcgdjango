import random
from datetime import date, timedelta

# Presupunem că ID-urile categoriilor din baza de date sunt între 1 și 5
categorii_ids = [1, 2, 3, 4, 5]
stari = ['nou', 'gradat', 'uzat']
prefixe = ['Pachet Booster', 'Carte Holo', 'Cutie Collector', 'Deck Structurat', 'Ediție Limitată', 'Promo Card']
teme = ['Charizard', 'Pikachu', 'Blue-Eyes', 'Dark Magician', 'Black Lotus', 'Luffy Gear 5', 'Mewtwo', 'Zoro']
taguri_posibile = ['holo', 'rar', 'editie-limitata', 'sigilat', 'vintage', 'promo', 'foil', 'colectie']

comenzi_sql = []

for i in range(1, 46):
    cat_id = random.choice(categorii_ids)
    titlu = f"{random.choice(prefixe)} {random.choice(teme)} #{i}"
    este_rar = random.choice([True, False])
    # Respectă constrângerea: dacă este_foarte_rar=True, prețul >= 50
    pret = round(random.uniform(55.0, 950.0), 2) if este_rar else round(random.uniform(10.0, 120.0), 2)
    stoc = random.randint(1, 40)
    stare = random.choice(stari)
    data_lansare = date(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
    tags_alese = random.sample(taguri_posibile, k=random.randint(1, 3))
    tags_sql = "ARRAY[" + ", ".join(f"'{t}'" for t in tags_alese) + "]::varchar[]"

    sql = (
        f"INSERT INTO trading_app_produs "
        f"(categorie_id, titlu, pret, stoc, este_foarte_rar, data_lansare, stare, tags, data_adaugare) "
        f"VALUES ({cat_id}, '{titlu}', {pret}, {stoc}, {str(este_rar).upper()}, "
        f"'{data_lansare}', '{stare}', {tags_sql}, NOW());"
    )
    comenzi_sql.append(sql)

with open("insert_produse.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(comenzi_sql))

print("S-au generat 45 de comenzi INSERT valide în fișierul insert_produse.sql!")