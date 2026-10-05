import snowflake.connector

conn = snowflake.connector.connect(
    account="ZUHWOAO-XR35810",
    user="ORKHOVEN",
    password="Bogfug=mibru8=nahnuq",
    role="ACCOUNTADMIN",
    database="NYC_TAXI",
    warehouse="NYC_TAXI_WH",
    schema="FINAL",
)

cursor = conn.cursor()

cursor.execute("""
    SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()
""")

print(cursor.fetchone())

cursor.close()
conn.close()