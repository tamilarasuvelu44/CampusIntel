import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "campusintel.db"

username = "admin"
password = "Admin@123"

hashed_password = generate_password_hash(password)

conn = sqlite3.connect(DATABASE)

cursor = conn.cursor()

cursor.execute("""
    UPDATE users
    SET password = ?, role = ?
    WHERE username = ?
""", (
    hashed_password,
    "admin",
    username
))

if cursor.rowcount == 0:

    cursor.execute("""
        INSERT INTO users
        (username, password, role)
        VALUES (?, ?, ?)
    """, (
        username,
        hashed_password,
        "admin"
    ))

    print("Admin account created.")

else:

    print("Admin account password and role reset.")

conn.commit()

conn.close()

print()
print("Username: admin")
print("Password: Admin@123")