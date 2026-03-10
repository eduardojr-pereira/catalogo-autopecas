import sqlite3


def salvar_oem(codigo):
    conn = sqlite3.connect("data/catalogo.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO oem (codigo) VALUES (?)",
        (codigo,)
    )
    conn.commit()
    conn.close()
    print(f"OEM salvo no banco: {codigo}")