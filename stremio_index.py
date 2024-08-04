from bs4 import BeautifulSoup
import requests
stremio = "http://web.stremio.com/"
x = requests.get(stremio)
print(x.text)

