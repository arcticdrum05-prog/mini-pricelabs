import subprocess
import sys

scripts = [
    "market_calendar.py",
    "generate_daily_prices.py",
    "apply_lead_time_adjustment.py",
    "estimate_occupancy.py",
    "optimize_prices.py",
]

for script in scripts:
    print(f"▶ Ejecutando {script}...")
    result = subprocess.run([sys.executable, script])

    if result.returncode != 0:
        print(f"❌ Error en {script}")
        sys.exit(1)

print("✅ Actualización diaria completada")
