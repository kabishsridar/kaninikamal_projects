# test_runner.py
import solutions

tests = [
    ("undo_text", [["type:A", "type:B", "undo", "type:C"]], "AC"),
    ("reverse_sentence", ["AI will change the world"], "world the change will AI"),
    ("is_balanced", ["{[()]}"], True),
    ("call_center", [["Call1", "Call2"], ["answer", "add:Call3", "answer"]], ["Call3"]),
    ("print_queue", [["Doc1", "Doc2", "Doc3"], ["print", "add:Doc4", "print", "print"]], ["Doc4"]),
    ("process_patients", [[(2, "John"), (5, "Alice"), (1, "Bob")]], ["Alice", "John", "Bob"]),
    ("process_jobs", [[(3, "Build"), (1, "Test"), (5, "Deploy")]], ["Deploy", "Build", "Test"]),
    ("browser_tabs", [["open:google.com", "open:youtube.com", "close", "open:github.com"]], ["open:google.com", "open:github.com"]),
    ("bank_tokens", [["T1", "T2"], ["serve", "add:T3", "serve", "serve"]], []),
    ("landing_order", [[(3, "FlightA"), (1, "FlightB"), (4, "FlightC")]], ["FlightC", "FlightA", "FlightB"])
]

def run_tests():
    passed = 0
    for func_name, args, expected in tests:
        func = getattr(solutions, func_name)
        try:
            if isinstance(args, list):
                result = func(*args)
            else:
                result = func(args)
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
