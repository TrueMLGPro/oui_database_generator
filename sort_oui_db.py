import os
import sqlite3

print("[i] Script started")
oui_db = "oui.db"

# Check if database is missing
if not os.path.exists(oui_db):
    print("[i] oui.db doesn't exist, generate the database first")
    exit(1)

# Connect to the database
conn = sqlite3.connect(oui_db)
c = conn.cursor()

# Execute the query to sort the values of the MAC column in ascending order
print("[i] Reordering values of column 'MAC' in ascending order")
c.execute("SELECT * FROM OUI ORDER BY MAC ASC")

# Fetch all the rows in sorted order
sorted_rows = c.fetchall()

# Rewrite the OUI table with the sorted values
print("[i] Replacing original data with sorted values")
c.execute("DELETE FROM OUI")
c.executemany("INSERT INTO OUI (MAC, VENDOR) VALUES (?, ?)", sorted_rows)

# Commit the changes to the database
print("[i] Applying changes and closing the database file")
conn.commit()
c.close()
conn.close()
print("[✓] Done!")