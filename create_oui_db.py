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

# Download oui.txt if it doesn't exist locally or if local txt's file size is 0 bytes
if not os.path.exists(local_oui_file):
	print("[!] oui.txt doesn't exist, downloading it!")
	download_db()
else:
	if os.stat(local_oui_file).st_size == 0:
		print("[!] oui.txt exists but is empty, downloading OUI data")
		os.remove(local_oui_file)
		download_db()
	print("[i] oui.txt exists, creating vendor database")

try:
	if os.path.exists(oui_db):
		# Remove the old DB if it exists
		print("[i] Old oui.db exists, removing it")
		os.remove(oui_db)
		# Create a new file
		print("[i] Creating oui.db")
		open(oui_db, "a").close()
except OSError as err:
	print(err)

conn = sqlite3.connect(oui_db)
c = conn.cursor()
c.execute("CREATE TABLE OUI (MAC text, VENDOR text)")
print("[i] Creating database table")

for line in open("oui.txt", encoding="utf-8"):
	r = re.search(r"^\s*([0-9A-Fa-f]*)\s*\(base 16\)\s*(.*)$", line)
	# If line matches the RegEx, write it to DB
	if r:
		mac = r.group(1)
		vendor = r.group(2).replace("'", "`").strip()
		try:
			line_count += 1
			print(f"[i] Inserting line {line_count} into table 'OUI'")
			c.execute(f"INSERT INTO OUI VALUES (\'{mac}\', \'{vendor}\')")
		except sqlite3.OperationalError as err:
			print(err)

print("[i] Applying changes and closing the database file")
conn.commit()
conn.close()
c.close()
print("[✓] Done!")