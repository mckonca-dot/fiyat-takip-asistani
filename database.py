import sqlite3
from datetime import datetime

DB_NAME = "fiyat_takip.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # YENİ SÜTUN EKLENDİ: owner_email
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            price REAL,
            last_checked DATETIME,
            owner_email TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ARTIK MAİL ADRESİNİ DE ALIYORUZ
def add_product(name, url, price, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Kontrolü hem URL hem de MAİL'e göre yap (Aynı ürünü başkası da ekleyebilir)
    cursor.execute("SELECT id FROM products WHERE url = ? AND owner_email = ?", (url, email))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE products SET price = ?, last_checked = ? WHERE id = ?", (price, now, existing[0]))
    else:
        cursor.execute("INSERT INTO products (name, url, price, last_checked, owner_email) VALUES (?, ?, ?, ?, ?)", (name, url, price, now, email))

    conn.commit()
    conn.close()