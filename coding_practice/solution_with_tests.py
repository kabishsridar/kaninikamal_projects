# test_runner.py

def problem1(feedbacks):
    from collections import Counter
    words = " ".join(feedbacks).split()
    return [word for word, _ in Counter(words).most_common(2)]

def problem2(visits):
    return len({user for user, _ in visits})

def problem3(inv_a, inv_b):
    merged = inv_a.copy()
    for item, qty in inv_b.items():
        merged[item] = merged.get(item, 0) + qty
    return merged

def problem4(all_ids, sold_ids):
    return all_ids - sold_ids

def problem5(scores):
    return sorted(scores, key=lambda x: x[1], reverse=True)

def problem6(words):
    from collections import defaultdict
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())

def problem7(team_a, team_b):
    return team_a & team_b

def problem8(orders):
    seen, duplicates = set(), set()
    for o in orders:
        if o in seen:
            duplicates.add(o)
        seen.add(o)
    return list(duplicates)

def problem9(movies, revenues):
    return dict(zip(movies, revenues))

def problem10(purchases):
    target = purchases["alice"]
    others = set()
    for cust, items in purchases.items():
        if cust != "alice":
            others |= items
    return others - target


# Test cases
tests = [
    ("Problem 1", problem1, (["good service", "fast delivery", "good product", "good service", "slow delivery"],), ["good", "service"]),
    ("Problem 2", problem2, ([("alice", "t1"), ("bob", "t2"), ("alice", "t3")],), 2),
    ("Problem 3", problem3, ({"apple": 10, "banana": 5}, {"banana": 7, "orange": 3}), {"apple": 10, "banana": 12, "orange": 3}),
    ("Problem 4", problem4, ({101, 102, 103, 104, 105}, {101, 103}), {102, 104, 105}),
    ("Problem 5", problem5, ([("Alice", 85), ("Bob", 90), ("Charlie", 78)],), [("Bob", 90), ("Alice", 85), ("Charlie", 78)]),
    ("Problem 6", problem6, (["listen", "silent", "enlist", "rat", "tar", "art"],), [["listen", "silent", "enlist"], ["rat", "tar", "art"]]),
    ("Problem 7", problem7, ({"python", "git", "docker"}, {"python", "aws", "docker"}), {"python", "docker"}),
    ("Problem 8", problem8, ([1001, 1002, 1003, 1002, 1004, 1001],), [1001, 1002]),
    ("Problem 9", problem9, (["A", "B", "C"], [1000, 2000, 1500]), {"A": 1000, "B": 2000, "C": 1500}),
    ("Problem 10", problem10, ({"alice": {"apple", "banana"}, "bob": {"banana", "orange"}, "charlie": {"apple", "orange", "banana"}},), {"orange"})
]

if __name__ == "__main__":
    for name, func, args, expected in tests:
        result = func(*args)
        if isinstance(expected, list):
            # Allow any order for list results
            try:
                passed = set(result) == set(expected)
            except Exception as e:
                print(e)
        else:
            passed = result == expected
        print(f"{name}: {'PASS' if passed else 'FAIL'} | Output: {result}")