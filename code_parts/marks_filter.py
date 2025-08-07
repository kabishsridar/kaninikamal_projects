import csv


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

def main():
    file_name = 'students.csv'
    min_mark = 80
    students = read_csv(file_name)
    passed_students = filter_students(students, min_mark)
    # print("Students who passed:")
    for s in passed_students:
        # print("Checking value in s: ", s)
        print(s['Name'], "-", s['Mark'])

if __name__ == "__main__":
    main()