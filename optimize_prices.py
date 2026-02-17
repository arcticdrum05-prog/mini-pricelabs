import pandas as pd
from pathlib import Path
import numpy as np

# =========================
# CARGAR DATA ACTUAL
# =========================
df = pd.read_csv("data/daily_prices_with_demand_2026.csv", parse_dates=["date"])

# =========================
# FUNCIÓN DE OCUPACIÓN (misma lógica)
# =========================
def occupancy_probability(season, date, test_price, base_price):
    base = 0.55

    if season == "high":
        base += 0.25
    elif season == "mid":
        base += 0.10
    else:
        base -= 0.10

    if pd.to_datetime(date).weekday() >= 4:
        base += 0.10

    price_ratio = test_price / base_price
    base -= (price_ratio - 1) * 0.8

    return max(0.05, min(0.95, base))


# =========================
# OPTIMIZACIÓN
# =========================
optimized_rows = []

for _, row in df.iterrows():

    base_price = row["recommended_price"]

    # probamos variaciones de precio
    test_prices = np.linspace(base_price * 0.7, base_price * 1.3, 9)

    best_price = base_price
    best_revenue = 0
    best_occ = 0

    for p in test_prices:
        occ = occupancy_probability(row["season"], row["date"], p, base_price)
        revenue = p * occ

        if revenue > best_revenue:
            best_revenue = revenue
            best_price = p
            best_occ = occ

    optimized_rows.append({
        "property": row["property"],
        "date": row["date"],
        "season": row["season"],
        "optimal_price": round(best_price, 2),
        "expected_occupancy": round(best_occ, 3),
        "expected_revenue": round(best_revenue, 2),
        "currency": row["currency"],
    })

opt_df = pd.DataFrame(optimized_rows)

# =========================
# GUARDAR RESULTADO
# =========================
Path("data").mkdir(exist_ok=True)
opt_df.to_csv("data/optimized_prices_2026.csv", index=False)

print("✅ Optimización completada")
print("Total precios optimizados:", len(opt_df))
