import streamlit as st
import requests
import pandas as pd

API_URL = "https://www.mdas.org/wp-json/wp/v2/annuaire?per_page=100&page={}"

def scrape_page(page):
    url = API_URL.format(page)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return []
    return r.json()

def extract_fields(item):
    return {
        "id": item.get("id"),
        "nom": item.get("title", {}).get("rendered"),
        "contenu_html": item.get("content", {}).get("rendered"),
        "slug": item.get("slug"),
        "lien": item.get("link")
    }

def scrape(n_pages):
    rows = []
    for p in range(1, n_pages + 1):
        st.write(f"📄 Page JSON {p}")
        data = scrape_page(p)
        if not data:
            st.warning(f"Aucune donnée page {p}. Fin.")
            break
        for item in data:
            rows.append(extract_fields(item))
    return pd.DataFrame(rows)

st.title("Scraper Annuaire MDAS (API JSON)")

pages = st.number_input("Pages à scraper", 1, 10, 3)

if st.button("Lancer"):
    df = scrape(pages)
    st.success(f"{len(df)} entrées récupérées ✔️")
    st.dataframe(df)
    st.download_button("Télécharger CSV", df.to_csv(index=False), "mdas_api.csv")
