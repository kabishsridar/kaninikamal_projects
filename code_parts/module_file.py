import csv

class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)

    def is_passed(self):
        return self.average() >= 40
    

def read_csv(file_name):
    """Reads a CSV file and returns list of rows"""
    data = []
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # print("checking reader: ",reader)
        for row in reader:
            print("Checking value in row: ", row)
            data.append(row)
    return data

def filter_students(students, min_mark):
    """Filters students who scored above min_mark"""
    result = []
    for student in students:
        if int(student['Mark']) >= min_mark:
            # print("Checking students: ", student)
            result.append(student)
    return result

file_name = 'students.csv'
min_mark = 80