import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CARGAR PRECIOS BASE
# =========================
df = pd.read_csv("data/daily_prices_2026.csv", parse_dates=["date"])

TODAY = pd.to_datetime(date.today())

# =========================
# CALCULAR LEAD TIME
# =========================
df["lead_days"] = (df["date"] - TODAY).dt.days

# =========================
# FACTORES DE ANTICIPACIÓN
# =========================
def lead_factor(days):
    if days > 90:
        return 0.90   # descuento early booking
    elif days > 30:
        return 1.00   # precio normal
    elif days > 7:
        return 1.10   # ligera subida
    elif days >= 0:
        return 0.85   # last minute discount
    else:
        return None   # fechas pasadas

df["lead_factor"] = df["lead_days"].apply(lead_factor)

# eliminar fechas pasadas
df = df.dropna(subset=["lead_factor"])

# =========================
# PRECIO AJUSTADO FINAL
# =========================
df["final_price"] = (df["recommended_price"] * df["lead_factor"]).round(2)

# =========================
# GUARDAR RESULTADO
# =========================
Path("data").mkdir(exist_ok=True)
df.to_csv("data/daily_prices_with_lead_2026.csv", index=False)

print("✅ Ajuste por anticipación aplicado")
print("Total registros activos:", len(df))
