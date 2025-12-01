import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.strasbourg.eu/annuaire-associations?p_p_id=listing_WAR_listingportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_listing_WAR_listingportlet_delta=10&_listing_WAR_listingportlet_resetCur=false&_listing_WAR_listingportlet_cur={}"

# ------------------------
# SCRAPER POUR 1 FICHE
# ------------------------
def parse_asso_block(block):
    data = {}

    # Nom
    title_tag = block.find("h3")
    data["nom"] = title_tag.get_text(strip=True) if title_tag else None

    # Catégorie / sous-titre
    subtitle = block.find("div", class_="subtitle")
    data["categorie"] = subtitle.get_text(strip=True) if subtitle else None

    # Description
    desc = block.find("div", class_="description")
    data["description"] = desc.get_text(" ", strip=True) if desc else None

    # Bloc détails (caché derrière "+")
    details = block.find("div", class_="contentDetails")
    if details:
        text = details.get_text("\n", strip=True)

        # extraction simple par mots clés
        for line in text.split("\n"):
            if "@" in line:
                data["email"] = line.strip()
            if "www" in line or "http" in line:
                data["site web"] = line.strip()
            if any(c.isdigit() for c in line) and len(line) > 6:
                if "Tel" in line or "tél" in line.lower():
                    data["telephone"] = line.strip()
                else:
                    data.setdefault("adresse", line.strip())

    return data

# ------------------------
# SCRAPER GLOBAL
# ------------------------
def scrape_annuaire(nb_pages):
    results = []

    for page in range(1, nb_pages + 1):
        url = BASE_URL.format(page)
        st.write(f"Scraping page {page}/{nb_pages}…")
        
        r = requests.get(url)
        if r.status_code != 200:
            st.error(f"Erreur page {page} : {r.status_code}")
            continue

        soup = BeautifulSoup(r.text, "lxml")

        blocks = soup.find_all("div", class_="resultsItem")
        if not blocks:
            st.warning(f"Aucun bloc trouvé page {page} (structure peut avoir changé).")
            continue

        for b in blocks:
            info = parse_asso_block(b)
            results.append(info)

        time.sleep(0.3)  # éviter de spammer le site

    return pd.DataFrame(results)


# ------------------------
# STREAMLIT UI
# ------------------------
st.title("📚 Scraper Annuaire des Associations – Strasbourg")

st.write("Entre combien de pages scraper (max ~154)")

nb_pages = st.number_input("Pages à scraper", min_value=1, max_value=154, value=5)

if st.button("🚀 Lancer le scraping"):
    df = scrape_annuaire(nb_pages)
    st.success(f"Scraping terminé : {len(df)} associations trouvées.")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger CSV", csv, "associations.csv", "text/csv")
