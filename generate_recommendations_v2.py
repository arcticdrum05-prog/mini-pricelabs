import psycopg2
from datetime import date, timedelta
import numpy as np

# =============================
# CONEXIÓN A POSTGRES (Railway)
# =============================
conn = psycopg2.connect(
    host="SWITCHYARD.PROXY.RLWY.NET",
    port="47433",
    dbname="railway",
    user="postgres",
    password="nZgHfBcHgqsBVyQXQbDahfvSNEpZfYNU"
)

cur = conn.cursor()

# =============================
# FUNCIÓN: probabilidad de reserva
# modelo simple de elasticidad
# =============================
def booking_probability(price, market_avg):
    if market_avg == 0:
        return 0.1

    ratio = price / market_avg

    # curva simple:
    # más caro que mercado → baja probabilidad
    # más barato → sube probabilidad
    prob = np.exp(-2 * (ratio - 1))

    # límites razonables
    return max(0.05, min(prob, 0.95))


# =============================
# OBTENER TODAS TUS PROPIEDADES
# =============================
cur.execute("""
    SELECT id, zone_id, bedrooms
    FROM properties;
""")

properties = cur.fetchall()

print(f"Procesando {len(properties)} propiedades...")

# =============================
# PARA CADA PROPIEDAD
# =============================
for property_id, zone_id, bedrooms in properties:

    print(f"→ Propiedad {property_id}")

    # -------------------------
    # precios promedio mercado
    # -------------------------
    cur.execute("""
        SELECT stay_date, AVG(price)
        FROM market_prices mp
        JOIN market_listings ml ON mp.listing_id = ml.id
        WHERE ml.zone_id = %s
          AND ml.bedrooms = %s
          AND stay_date >= CURRENT_DATE
        GROUP BY stay_date
        ORDER BY stay_date
        LIMIT 30;
    """, (zone_id, bedrooms))

    market_rows = cur.fetchall()

    # -------------------------
    # optimización por fecha
    # -------------------------
    for stay_date, avg_price in market_rows:

        avg_price = float(avg_price)

        # rango de precios a probar (70% a 130% del mercado)
        candidate_prices = [float(p) for p in np.linspace(avg_price * 0.7, avg_price * 1.3, 20)]

        best_price = avg_price
        best_revenue = 0
        best_prob = 0

        for price in candidate_prices:
            prob = booking_probability(price, avg_price)
            revenue = price * prob

            if revenue > best_revenue:
                best_revenue = revenue
                best_price = price
                best_prob = prob

        # guardar recomendación
        cur.execute("""
            INSERT INTO price_recommendations
            (property_id, date, recommended_price,
             expected_occupancy, expected_revenue,
             market_avg_price, model_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (property_id, date, model_version)
            DO UPDATE SET
                recommended_price = EXCLUDED.recommended_price,
                expected_occupancy = EXCLUDED.expected_occupancy,
                expected_revenue = EXCLUDED.expected_revenue,
                market_avg_price = EXCLUDED.market_avg_price;
        """, (
            property_id,
            stay_date,
            float(round(best_price, 2)),
float(round(best_prob, 3)),
float(round(best_revenue, 2)),
float(round(avg_price, 2)),
            "v2_elasticity"
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Recomendaciones inteligentes generadas")
