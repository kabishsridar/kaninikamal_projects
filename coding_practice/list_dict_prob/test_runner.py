# test_runner.py
import solutions

tests = [
    ("extract_emails", [["John Doe <john@example.com>", "Jane Smith <jane.smith@work.org>"]],
     ["john@example.com", "jane.smith@work.org"]),
    
    ("count_unique_visitors", [["A123", "B456", "A123"]], 2),

    ("total_sales_per_product", [[("Laptop", 1200), ("Phone", 800), ("Laptop", 1400)]],
     {"Laptop": 2600, "Phone": 800}),

    ("sort_events_by_time", [[("Meeting", "10:00"), ("Lunch", "13:00"), ("Call", "09:30")]],
     [("Call", "09:30"), ("Meeting", "10:00"), ("Lunch", "13:00")]),

    ("find_country_by_city", [{"India": ["Delhi", "Mumbai"], "USA": ["NY"]}, "Mumbai"], "India"),

    ("find_missing_products", [{101, 102, 103}, {101, 103}], {102}),

    ("filter_students_by_grade", [{"Alice": 85, "Bob": 67}, 75], ["Alice"]),

    ("merge_contact_lists", [["a@gmail.com", "b@yahoo.com"], ["b@yahoo.com", "c@hotmail.com"]],
     ["a@gmail.com", "b@yahoo.com", "c@hotmail.com"]),

    ("invert_dict", [{"IT": "Alice", "HR": "Bob"}], {"Alice": "IT", "Bob": "HR"}),

    ("word_frequency", ["apple banana apple orange banana apple"],
     [("apple", 3), ("banana", 2), ("orange", 1)])
]

def run_tests():
    passed = 0
    for func_name, args, expected in tests:
        func = getattr(solutions, func_name)
        try:
            result = func(*args) if isinstance(args, list) else func(args)
            if result == expected:
                print(f"[PASS] {func_name}")
                passed += 1
            else:
                print(f"[FAIL] {func_name} → Expected {expected}, Got {result}")
        except Exception as e:
            print(f"[ERROR] {func_name} → {e}")
    print(f"\n✅ Passed {passed}/{len(tests)} tests")

if __name__ == "__main__":
    run_tests()
