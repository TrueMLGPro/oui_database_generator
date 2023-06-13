import os
import re
import sqlite3
import urllib
import urllib.request

print("[i] Script started")
url = 'https://standards-oui.ieee.org/oui/oui.txt'
oui_db = "oui.db"
local_oui_file = "oui.txt"
line_count = 0

def download_db():
	with urllib.request.urlopen(url) as response, open(local_oui_file, 'wb') as out_file:
		# Response data stored in bytes
		data = response.read()
		out_file.write(data)
		out_file.close()
		response.close()
	print("[!] Download finished!")

# Download oui.txt if it doesn't exist locally or if local txt file is 0 bytes in size
if not os.path.exists(local_oui_file):
	print(f"[!] {local_oui_file} doesn't exist, downloading it!")
	download_db()
else:
	if os.stat(local_oui_file).st_size == 0:
		print(f"[!] {local_oui_file} exists but is empty, downloading OUI data")
		os.remove(local_oui_file)
		download_db()
	print(f"[i] {local_oui_file} exists, creating vendor database")

try:
	if os.path.exists(oui_db):
		# Remove the old DB if it exists
		print(f"[i] Old {oui_db} exists, removing it")
		os.remove(oui_db)
		# Create a new file
		print(f"[i] Creating {oui_db}")
		open(oui_db, "a").close()
except OSError as err:
	print(err)

conn = sqlite3.connect(oui_db)
cursor = conn.cursor()
print("[i] Creating database table 'oui'")
cursor.execute("CREATE TABLE oui (mac TEXT, vendor TEXT)")

for line in open(local_oui_file, encoding="utf-8"):
	r = re.search(r"^\s*([0-9A-Fa-f]*)\s*\(base 16\)\s*(.*)$", line)
	# If line matches the RegEx, write it to DB
	if r:
		mac = r.group(1)
		vendor = r.group(2).replace("'", "`").strip()
		try:
			line_count += 1
			print(f"[i] Inserting line {line_count} into table 'oui'")
			cursor.execute(f"INSERT INTO oui VALUES (\'{mac}\', \'{vendor}\')")
		except sqlite3.OperationalError as err:
			print(err)

print("[i] Applying changes and closing the database file")
conn.commit()
conn.close()
print("[✓] Done!")