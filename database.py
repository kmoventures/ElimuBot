import os
import sqlite3

class ElimuDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "elimu.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            role TEXT
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            phone TEXT,
            subjects TEXT,
            hourly_rate INTEGER,
            experience INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            phone TEXT,
            level TEXT,
            subject TEXT,
            budget INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        self.conn.commit()

    def save_user(self, telegram_id, role):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, role)
        VALUES (?, ?)
        """, (telegram_id, role))
        self.conn.commit()
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()[0]

    def save_tutor(self, telegram_id, full_name, phone, subjects, hourly_rate, experience=None):
        user_id = self.save_user(telegram_id, "tutor")
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO tutors (user_id, full_name, phone, subjects, hourly_rate, experience)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, full_name, phone, subjects, hourly_rate, experience))
        self.conn.commit()

    def save_student(self, telegram_id, full_name, phone, level, subject, budget):
        user_id = self.save_user(telegram_id, "student")
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO students (user_id, full_name, phone, level, subject, budget)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, full_name, phone, level, subject, budget))
        self.conn.commit()

    def get_matching_tutors(self, subject, budget, limit=3):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT tutors.full_name, tutors.phone, tutors.subjects, tutors.hourly_rate, tutors.experience, users.telegram_id
        FROM tutors
        JOIN users ON tutors.user_id = users.id
        WHERE tutors.subjects LIKE ? AND tutors.hourly_rate <= ?
        ORDER BY tutors.hourly_rate ASC
        LIMIT ?
        """, (f"%{subject}%", budget, limit))
        return cursor.fetchall()


    def get_all_tutors(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT tutors.*, users.telegram_id
        FROM tutors
        JOIN users ON tutors.user_id = users.id
        """)
        return cursor.fetchall()

    def get_all_students(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT students.*, users.telegram_id
        FROM students
        JOIN users ON students.user_id = users.id
        """)
        return cursor.fetchall()

if __name__ == "__main__":
    db = ElimuDatabase()
    print("✅ Database initialized at:", db.db_path)
