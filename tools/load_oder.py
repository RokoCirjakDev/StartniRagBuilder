import oracledb
import pandas as pd
import os


connection = oracledb.connect(user="IPPORTAL", password="IPPORTAL", dsn="IP")

query = """
SELECT 
  s.OPIS, 
  s.PRIMJEDBA, 
  u.APLIKACIJA
FROM 
  stavkaupita s
JOIN 
  upitzapodrsku u ON s.upitzapodrsku = u.upitzapodrsku
WHERE 
  s.OPIS IS NOT NULL 
  AND s.PRIMJEDBA IS NOT NULL 
  AND u.APLIKACIJA IS NOT NULL 
  AND u.upitzapodrsku IS NOT NULL
"""

df = pd.read_sql(query, con=connection)

os.makedirs("unos/cvs-ode", exist_ok=True)

df.to_csv("unos/cvs-ode/ode.txt", sep='|', encoding='utf-8', index=False)

print("✅ Exported to unos/cvs-ode/export.txt")
