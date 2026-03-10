import requests
from bs4 import BeautifulSoup
from scraper.detect_oem import detectar_oem 
from database.insert_data import salvar_oem

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extrair_texto(url):
    response = requests.get(url, 
                            verify=False
                            ) #ignorar SSL somente para testar
    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text()
    return texto


def processar_url(url):
    texto = extrair_texto(url)
    oems = detectar_oem(texto)
    print("URL analisada:", url)
    print("OEM encontrados:", oems)
    
    for oem in oems:
        salvar_oem(oem)
    
    print("--------------")


if __name__ == "__main__":
    urls = [
        "https://example.com"
    ]
    for url in urls:
        processar_url(url)