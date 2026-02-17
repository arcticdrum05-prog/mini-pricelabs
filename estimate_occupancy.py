import pandas as pd
from pathlib import Path

# =========================
# CARGAR PRECIOS ACTUALES
# =========================
df = pd.read_csv("data/daily_prices_with_lead_2026.csv", parse_dates=["date"])

# =========================
# FUNCIÓN DE OCUPACIÓN
# =========================
def occupancy_probability(row):
    base = 0.55  # ocupación promedio destino playa

    # temporada
    if row["season"] == "high":
        base += 0.25
    elif row["season"] == "mid":
        base += 0.10
    else:
        base -= 0.10

    # fin de semana
    if row["date"].weekday() >= 4:
        base += 0.10

    # efecto precio (elasticidad simple)
    price_ratio = row["final_price"] / row["recommended_price"]
    base -= (price_ratio - 1) * 0.8

    # límites realistas
    return max(0.05, min(0.95, base))


df["occupancy_prob"] = df.apply(occupancy_probability, axis=1)

# =========================
# INGRESO ESPERADO
# =========================
df["expected_revenue"] = (df["final_price"] * df["occupancy_prob"]).round(2)

# =========================
# GUARDAR
# =========================
Path("data").mkdir(exist_ok=True)
df.to_csv("data/daily_prices_with_demand_2026.csv", index=False)

print("✅ Probabilidad de ocupación estimada")
print("Registros:", len(df))
