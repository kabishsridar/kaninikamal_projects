from module_file import read_csv, filter_students

def main():
    file_name = 'students_functional.csv'
    min_mark = 80
    students = read_csv(file_name)
    passed_students = filter_students(students, min_mark)
    # print("Students who passed:")
    for s in passed_students:
        # print("Checking value in s: ", s)
        print(s['Name'], "-", s['Mark'])

if __name__ == "__main__":
    main()