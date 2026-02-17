import psycopg2
from datetime import date, timedelta
import random

conn = psycopg2.connect(
    host="SWITCHYARD.PROXY.RLWY.NET",
    port="47433",
    dbname="railway",
    user="postgres",
    password="nZgHfBcHgqsBVyQXQbDahfvSNEpZfYNU"
)

cur = conn.cursor()

# 1. Insertar 5 propiedades comparables en Tulum/Tankah
for i in range(5):
    cur.execute("""
        INSERT INTO market_listings (external_id, zone_id, bedrooms, bathrooms, max_guests, rating)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        f"listing_{i}",
        1,                      # asumiendo zona 1 = Tulum/Tankah
        random.choice([1, 2]),
        random.choice([1, 2]),
        random.choice([2, 4, 6]),
        round(random.uniform(4.3, 4.9), 2)
    ))

    listing_id = cur.fetchone()[0]

    # 2. Crear precios para los próximos 30 días
    for d in range(30):
        stay_date = date.today() + timedelta(days=d)
        price = random.randint(1500, 4500)

        cur.execute("""
            INSERT INTO market_prices (listing_id, stay_date, snapshot_date, price, is_available)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            listing_id,
            stay_date,
            date.today(),
            price,
            True
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Datos de mercado insertados correctamente")
