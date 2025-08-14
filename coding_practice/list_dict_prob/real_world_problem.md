1. Customer Email Extractor (List + String Processing)

Dataset Example:

customers = [
    "John Doe <john@example.com>",
    "Jane Smith <jane.smith@work.org>",
    "Foo Bar <foo@bar.net>"
]


Task:
extract_emails(customers) → return list of emails only.

2. Unique Visitors Counter (Set usage)

Dataset Example:

visitors = ["A123", "B456", "A123", "C789", "B456", "D000"]


Task:
count_unique_visitors(visitors) → return count of unique visitors.

3. Top-Selling Products (Dict usage)

Dataset Example:

sales = [
    ("Laptop", 1200),
    ("Phone", 800),
    ("Laptop", 1400),
    ("Tablet", 600)
]


Task:
total_sales_per_product(sales) → return dict:

{"Laptop": 2600, "Phone": 800, "Tablet": 600}

4. Event Schedule Merger (List of Tuples sorting)

Dataset Example:

events = [
    ("Meeting", "10:00"),
    ("Lunch", "13:00"),
    ("Call", "09:30")
]


Task:
sort_events_by_time(events) → sort by time, return list of tuples.

5. Country-City Lookup (Dict reverse mapping)

Dataset Example:

country_city = {
    "India": ["Delhi", "Mumbai", "Chennai"],
    "USA": ["New York", "Chicago", "LA"]
}


Task:
find_country_by_city(country_city, "Mumbai") → return "India"

6. Missing Product IDs (Set difference)

Dataset Example:

all_ids = {101, 102, 103, 104, 105}
sold_ids = {101, 103, 105}


Task:
find_missing_products(all_ids, sold_ids) → return {102, 104}

7. Student Grade Filter (Dict + List comprehension)

Dataset Example:

grades = {
    "Alice": 85,
    "Bob": 67,
    "Charlie": 90,
    "David": 72
}


Task:
filter_students_by_grade(grades, 75) → return list of names scoring ≥ 75.

8. Merge Contact Lists (List + Set union)

Dataset Example:

contacts_a = ["alice@gmail.com", "bob@yahoo.com"]
contacts_b = ["bob@yahoo.com", "charlie@hotmail.com"]


Task:
merge_contact_lists(contacts_a, contacts_b) → return sorted unique list.

9. Invert Dictionary (Dict comprehension)

Dataset Example:

dept_emp = {"IT": "Alice", "HR": "Bob", "Sales": "Charlie"}


Task:
invert_dict(dept_emp) → return

{"Alice": "IT", "Bob": "HR", "Charlie": "Sales"}

10. Word Frequency Counter (Dict + Sorting)

Dataset Example:

text = "apple banana apple orange banana apple"


Task:
word_frequency(text) → return list of tuples sorted by frequency desc:

[("apple", 3), ("banana", 2), ("orange", 1)]

## How You’ll Work

Step 1 → Create solutions.py with all 10 empty functions.

Step 2 → Write your solution for each problem.

Step 3 → Run

python test_runner.py


Step 4 → See pass/fail results, fix until all green ✅
