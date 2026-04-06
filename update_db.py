import sqlite3

conn = sqlite3.connect('student_analytics.db')
cur = conn.cursor()

updates = {
    '1': 'TVE21CS001',
    '5': 'MAC20ME005',
    '68': 'KTE19CE031',
    '78': 'TVE21CS002',
    '9': 'MAC20ME006',
    '37': 'KTE19CE032'
}

for old, new in updates.items():
    cur.execute("UPDATE students SET roll_no=? WHERE roll_no=?", (new, old))

conn.commit()
conn.close()
print("Updated database!")
