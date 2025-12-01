import requests
from bs4 import BeautifulSoup

url = "https://www.mdas.org/annuaire/page/2/"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
print(r.text[:3000])
