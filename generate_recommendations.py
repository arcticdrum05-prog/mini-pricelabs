import psycopg2
from datetime import date

conn = psycopg2.connect(
    host="SWITCHYARD.PROXY.RLWY.NET",
    port="47433",
    dbname="railway",
    user="postgres",
    password="nZgHfBcHgqsBVyQXQbDahfvSNEpZfYNU"
)

cur = conn.cursor()

# Obtener promedio de mercado por fecha futura
cur.execute("""
    SELECT
        stay_date,
        AVG(price) as avg_price
    FROM market_prices
    WHERE stay_date >= CURRENT_DATE
    GROUP BY stay_date
    ORDER BY stay_date
    LIMIT 30;
""")

rows = cur.fetchall()

PROPERTY_ID = 1  # luego lo haremos dinámico

for stay_date, avg_price in rows:
    recommended_price = round(float(avg_price) * 0.95, 2)
  # 5% debajo del mercado

    cur.execute("""
        INSERT INTO price_recommendations
        (property_id, date, recommended_price, market_avg_price, model_version)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (property_id, date, model_version)
        DO NOTHING;
    """, (
        PROPERTY_ID,
        stay_date,
        recommended_price,
        avg_price,
        "v1_simple_avg"
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Recomendaciones generadas correctamente")
