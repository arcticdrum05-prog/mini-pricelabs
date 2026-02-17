import subprocess
import sys
import time

scripts = [
    "market_calendar.py",
    "generate_daily_prices.py",
    "apply_lead_time_adjustment.py",
    "estimate_occupancy.py",
    "optimize_prices.py",
]

while True:
    print("🚀 Iniciando actualización diaria...")

    for script in scripts:
        print(f"▶ Ejecutando {script}...")
        result = subprocess.run([sys.executable, script])

        if result.returncode != 0:
            print(f"❌ Error en {script}")
            sys.exit(1)

    print("✅ Actualización completada. Esperando 24h...")
    time.sleep(60 * 60 * 24)  # 24 horas
