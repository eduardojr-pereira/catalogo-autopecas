from scraper.detect_oem import detectar_oem 

# teste simples
if __name__ == "__main__":

    texto_exemplo = """
    Pastilha de freio dianteira Bosch BP1101
    Compatível com Toyota Corolla
    OEM: 04465-0F010
    Equivalentes: TRW GDB3421, Cobreq N1760
    """

    resultado = detectar_oem(texto_exemplo)

    print("OEM detectados:")
    print(resultado)