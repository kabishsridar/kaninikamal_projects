import csv

class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)

    def is_passed(self):
        return self.average() >= 40

students = []

with open("students.csv", newline='') as file:
    reader = csv.reader(file)
    next(reader)  # skip header
    for row in reader:
        name = row[0]
        marks = list(map(int, row[1:]))
        student = Student(name, marks)
        students.append(student)

for student in students:
    print(f"{student.name} - Average: {student.average():.2f}, Passed: {student.is_passed()}")