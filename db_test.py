import psycopg2

conn = psycopg2.connect(
    host="SWITCHYARD.PROXY.RLWY.NET",
    port="47433",
    dbname="railway",
    user="postgres",
    password="nZgHfBcHgqsBVyQXQbDahfvSNEpZfYNU"
)

cur = conn.cursor()
cur.execute("SELECT NOW();")
print("Conexión exitosa:", cur.fetchone())

cur.close()
conn.close()
