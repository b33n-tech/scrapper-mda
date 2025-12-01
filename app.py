import streamlit as st
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE = "https://www.mdas.org/annuaire/page/{}/"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_page(driver, page):
    url = BASE.format(page)
    driver.get(url)
    time.sleep(2)  # laisser le JS charger

    blocks = driver.find_elements(By.CSS_SELECTOR, "div.entry-content *")
    if not blocks:
        return []

    results = []
    current = None

    for el in blocks:
        txt = el.text.strip()

        if not txt:
            continue

        # Début d’une nouvelle asso → titres "### NomAsso"
        if txt.startswith("### "):
            if current:
                results.append(current)
            current = {"nom": txt.replace("### ", "").strip()}
            continue

        if current is None:
            continue

        # Catégories (MAJUSCULES avec "-")
        if " - " in txt and txt.upper() == txt:
            current["categorie"] = txt
            continue

        # Site web
        if txt.startswith("Site internet"):
            current["site"] = txt.split(":", 1)[1].strip() if ":" in txt else txt
            continue

        # Coordonnées / email / téléphone / adresse
        if "@" in txt or "Tél" in txt or any(c.isdigit() for c in txt):
            current.setdefault("coordonnees", []).append(txt)
            continue

    if current:
        results.append(current)

    return results

def scrape(n_pages):
    driver = get_driver()
    all_assos = []

    for p in range(1, n_pages + 1):
        st.write(f"📄 Page {p}…")
        try:
            assos = scrape_page(driver, p)
            st.write(f"➡️ {len(assos)} associations trouvées")
            all_assos.extend(assos)
        except Exception as e:
            st.error(f"Erreur page {p} : {e}")

    driver.quit()
    return pd.DataFrame(all_assos)

st.title("📚 Scraper Annuaire MDAS (Selenium)")

pages = st.number_input("Pages à scraper", 1, 154, 3)

if st.button("Lancer"):
    df = scrape(pages)
    st.success(f"{len(df)} associations récupérées ✔️")
    st.dataframe(df)
    st.download_button("Télécharger CSV", df.to_csv(index=False), "assos_mdas.csv")
