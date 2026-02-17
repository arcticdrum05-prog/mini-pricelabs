import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 12, 31)

# Temporadas típicas Riviera Maya
HIGH_SEASON_MONTHS = [1, 2, 3, 4, 12]
MID_SEASON_MONTHS = [7, 8]
LOW_SEASON_MONTHS = [5, 6, 9, 10, 11]

# Factores de temporada
SEASON_FACTORS = {
    "high": 1.4,
    "mid": 1.15,
    "low": 0.85,
}

WEEKEND_FACTOR = 1.15

# =========================
# GENERAR CALENDARIO
# =========================

dates = []
current = START_DATE

while current <= END_DATE:
    weekday = current.weekday()
    month = current.month

    # temporada
    if month in HIGH_SEASON_MONTHS:
        season = "high"
    elif month in MID_SEASON_MONTHS:
        season = "mid"
    else:
        season = "low"

    season_factor = SEASON_FACTORS[season]

    # fin de semana
    weekend_factor = WEEKEND_FACTOR if weekday >= 4 else 1.0

    dates.append({
        "date": current,
        "month": month,
        "weekday": weekday,
        "season": season,
        "season_factor": season_factor,
        "weekend_factor": weekend_factor,
    })

    current += timedelta(days=1)

df = pd.DataFrame(dates)

# =========================
# GUARDAR
# =========================

Path("data").mkdir(exist_ok=True)
df.to_csv("data/market_calendar_2026.csv", index=False)

print("✅ Calendario de mercado generado: data/market_calendar_2026.csv")
print("Total días:", len(df))
