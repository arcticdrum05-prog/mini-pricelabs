import pandas as pd
from pathlib import Path

# =========================
# RUTAS
# =========================
INPUT_FILE = "reservas.xlsx"
OUTPUT_FILE = "data/reservations_clean.csv"

# =========================
# LEER EXCEL
# =========================
df = pd.read_excel(INPUT_FILE)

print(f"Filas originales: {len(df)}")

# =========================
# SELECCIONAR COLUMNAS ÚTILES
# =========================
cols = [
    "Check in",
    "Check out",
    "NOCHES",
    "DEPARTAMENTO",
    "PAIS",
    "#ADULTS",
    "#CHILDRENS OR BABIES",
    "OTA",
    "BOOKED",
    "TARIFA DIARIA USD",
]

df = df[cols].copy()

# =========================
# CONVERTIR FECHAS
# =========================
df["Check in"] = pd.to_datetime(df["Check in"], errors="coerce")
df["Check out"] = pd.to_datetime(df["Check out"], errors="coerce")
df["BOOKED"] = pd.to_datetime(df["BOOKED"], errors="coerce")

# eliminar filas sin fechas válidas
df = df.dropna(subset=["Check in", "Check out", "BOOKED"])


# =========================
# VARIABLES NUEVAS IMPORTANTES
# =========================

# Anticipación de reserva (lead time)
df["lead_time_days"] = (df["Check in"] - df["BOOKED"]).dt.days

# Huéspedes totales
df["guests"] = df["#ADULTS"].fillna(0) + df["#CHILDRENS OR BABIES"].fillna(0)

# Mes de estancia
df["stay_month"] = df["Check in"].dt.month

# Día de la semana (0=Lunes, 6=Domingo)
df["stay_weekday"] = df["Check in"].dt.weekday

# Precio
# limpiar texto de precio (quitar $, comas, espacios, etc.)
df["price_usd"] = (
    df["TARIFA DIARIA USD"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

# convertir a número
df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")


# =========================
# LIMPIEZA BÁSICA
# =========================

df = df.dropna(subset=["price_usd", "lead_time_days"])
df = df[df["price_usd"] > 0]
df = df[df["lead_time_days"] >= 0]

print(f"Filas limpias: {len(df)}")

# =========================
# CREAR CARPETA data SI NO EXISTE
# =========================
Path("data").mkdir(exist_ok=True)

# =========================
# GUARDAR CSV LIMPIO
# =========================
df.to_csv(OUTPUT_FILE, index=False)

print("✅ Dataset limpio guardado en:", OUTPUT_FILE)
