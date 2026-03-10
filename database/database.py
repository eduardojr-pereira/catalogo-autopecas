import sqlite3

conn = sqlite3.connect("data/catalogo.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    modelo TEXT,
    ano TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sistemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pecas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    sistema_id INTEGER,
    FOREIGN KEY (sistema_id) REFERENCES sistemas(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS oem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    peca_id INTEGER,
    FOREIGN KEY (peca_id) REFERENCES pecas(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS equivalentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fabricante TEXT,
    codigo TEXT,
    oem_id INTEGER,
    FOREIGN KEY (oem_id) REFERENCES oem(id)
)
""")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")