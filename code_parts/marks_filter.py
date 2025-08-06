import csv


def read_csv(file_name):
    """Reads a CSV file and returns list of rows"""
    data = []
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def filter_students(students, min_mark):
    """Filters students who scored above min_mark"""
    result = []
    for student in students:
        if int(student['Mark']) >= min_mark:
            result.append(student)
    return result

def main():
    file_name = 'students.csv'
    min_mark = 80
    students = read_csv(file_name)
    passed_students = filter_students(students, min_mark)
    print("Students who passed:")
    for s in passed_students:
        print(s['Name'], "-", s['Mark'])

if __name__ == "__main__":
    main()