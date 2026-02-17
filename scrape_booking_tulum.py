import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONEXIÓN DB (Railway env)
# =========================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

# =========================
# URL búsqueda Booking Tulum
# =========================
URL = "https://www.booking.com/searchresults.html?ss=Tulum"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

# =========================
# EXTRAER TARJETAS
# =========================
cards = soup.select('[data-testid="property-card"]')

print(f"Encontradas {len(cards)} propiedades")

conn = get_connection()
cur = conn.cursor()

for i, card in enumerate(cards[:20]):  # solo 20 → scraping ligero
    try:
        name_tag = card.select_one('[data-testid="title"]')
        price_tag = card.select_one('[data-testid="price-and-discounted-price"]')

        if not name_tag or not price_tag:
            continue

        name = name_tag.get_text(strip=True)

        # limpiar precio
        price_text = price_tag.get_text(strip=True)
        price_number = "".join(c for c in price_text if c.isdigit())

        if not price_number:
            continue

        price = int(price_number)

        # insertar listing si no existe
        cur.execute("""
            INSERT INTO market_listings (external_id, zone_id, bedrooms)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id;
        """, (f"booking_{i}", 1, 1))

        result = cur.fetchone()

        if result:
            listing_id = result[0]
        else:
            cur.execute("""
                SELECT id FROM market_listings
                WHERE external_id = %s
                LIMIT 1;
            """, (f"booking_{i}",))
            listing_id = cur.fetchone()[0]

        # insertar precio
        cur.execute("""
            INSERT INTO market_prices
            (listing_id, stay_date, snapshot_date, price, is_available)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            listing_id,
            date.today(),
            date.today(),
            price,
            True
        ))

    except Exception as e:
        print("Error en card:", e)

conn.commit()
cur.close()
conn.close()

print("✅ Scraping terminado")
