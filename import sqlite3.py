import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("instance/school.db")
conn.execute("UPDATE users SET password_hash = ? WHERE role = 'admin'", (generate_password_hash("admin@123"),))
conn.execute("UPDATE users SET password_hash = ? WHERE role = 'principal'", (generate_password_hash("principal@123"),))
conn.commit()
conn.close()
print("Passwords reset successfully")