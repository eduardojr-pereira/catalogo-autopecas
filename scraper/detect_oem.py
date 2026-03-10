import re


def detectar_oem(texto):
    padroes = [
        r'\b\d{5}-[A-Z0-9]{5}\b',      # Toyota exemplo 04465-0F010
        r'\b[A-Z0-9]{9,12}\b',        # VW / GM códigos longos
        r'\b\d{3,5}[A-Z]{1,2}\d{2,5}\b' # padrões mistos
    ]

    oems = []
    for padrao in padroes:
        encontrados = re.findall(padrao, texto)
        oems.extend(encontrados)
    return list(set(oems))


