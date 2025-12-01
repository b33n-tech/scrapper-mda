import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE = "https://www.mdas.org/annuaire/page/{page}/"

def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", {"id":"content"}) or soup  # ajuster si id différent
    text = content.get_text("\n", strip=True)
    lines = text.split("\n")
    assos = []
    curr = None

    for line in lines:
        # détecter début asso : ligne commençant par '### '
        if line.startswith("### "):
            if curr:
                assos.append(curr)
            curr = {"nom": line[4:].strip()}
            continue
        if curr is None:
            continue

        # catégories
        # si ligne en MAJUSCULES avec un '-'
        if " - " in line and line.upper() == line:
            curr["categorie"] = line.strip()
            continue
        # site internet
        if line.startswith("Site internet"):
            parts = line.split(":",1)
            if len(parts)>1:
                curr["site"] = parts[1].strip()
            continue
        # coordonnées / contact / adresse / email / téléphone
        if "Tél" in line or "téléphone" in line or "@" in line or any(c.isdigit() for c in line):
            curr.setdefault("coordonnees", []).append(line.strip())
            continue

    if curr:
        assos.append(curr)
    return assos

def scrape(n_pages):
    all_assos = []
    for p in range(1, n_pages+1):
        url = BASE.format(page=p)
        r = requests.get(url)
        if r.status_code != 200:
            st.error(f"Erreur page {p}: {r.status_code}")
            continue
        assos = parse_page(r.text)
        st.write(f"Page {p}: {len(assos)} associations trouvées")
        all_assos.extend(assos)
        time.sleep(0.2)
    return pd.DataFrame(all_assos)

st.title("Scraper MDAS annuaire")
n = st.number_input("Pages à scraper", min_value=1, max_value=154, value=5)
if st.button("Go"):
    df = scrape(n)
    st.dataframe(df)
    st.download_button("Télécharger CSV", df.to_csv(index=False), "mdas_assos.csv", "text/csv")
