# view_db.py
from database import ElimuDatabase

db = ElimuDatabase()

print("📚 Tutors:")
for tutor in db.get_all_tutors():
    print(tutor)

print("\n🎓 Students:")
for student in db.get_all_students():
    print(student)
