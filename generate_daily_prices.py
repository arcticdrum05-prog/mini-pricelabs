import pandas as pd
from pathlib import Path

# =========================
# CARGAR CALENDARIO
# =========================
calendar = pd.read_csv("data/market_calendar_2026.csv", parse_dates=["date"])

# =========================
# CONFIGURACIÓN DE PROPIEDADES
# =========================

properties = [
    {"name": "Tulum Studio", "base_price": 900, "currency": "MXN"},
    {"name": "Tulum 1BR", "base_price": 1500, "currency": "MXN"},
    {"name": "Tulum 2BR", "base_price": 2000, "currency": "MXN"},
    {"name": "Tankah 1BR Beachfront", "base_price": 250, "currency": "USD"},
    {"name": "Tankah 2BR Beachfront", "base_price": 500, "currency": "USD"},
    {"name": "Tankah 3BR Beachfront", "base_price": 750, "currency": "USD"},
]

# =========================
# GENERAR PRECIOS
# =========================

rows = []

for prop in properties:
    for _, day in calendar.iterrows():

        price = (
            prop["base_price"]
            * day["season_factor"]
            * day["weekend_factor"]
        )

        rows.append({
            "property": prop["name"],
            "date": day["date"],
            "season": day["season"],
            "recommended_price": round(price, 2),
            "currency": prop["currency"],
        })

df = pd.DataFrame(rows)

# =========================
# GUARDAR RESULTADO
# =========================

Path("data").mkdir(exist_ok=True)
df.to_csv("data/daily_prices_2026.csv", index=False)

print("✅ Precios diarios generados")
print("Total registros:", len(df))
