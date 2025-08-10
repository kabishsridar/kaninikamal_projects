from module_file import Student
from csv import reader

students = []

with open("students.csv", newline='') as file:
    reader = reader(file)
    next(reader)  # skip header
    for row in reader:
        name = row[0]
        marks = list(map(int, row[1:]))
        student = Student(name, marks)
        students.append(student)

for student in students:
    print(f"{student.name} - Average: {student.average():.2f}, Passed: {student.is_passed()}")