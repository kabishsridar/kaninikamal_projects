🎯 Real-World Problem Pack – Progressive Difficulty

1. Undo Feature in Text Editor (Stack)

Dataset Example:

ops = ["type:A", "type:B", "undo", "type:C"]


Task:
Simulate text editing where:

"type:X" → add X to text

"undo" → remove last character

Return final string.

2. Reverse Sentence Words (Stack)

Dataset Example:

sentence = "AI will change the world"


Task:
Reverse word order using a stack → "world the change will AI"

3. Balanced Brackets Checker (Stack)

Dataset Example:

expr = "{[()]}"


Task:
Check if brackets are balanced (supports {}, [], ()).

4. Call Center Simulation (Queue)

Dataset Example:

calls = ["Call1", "Call2"]
ops = ["answer", "add:Call3", "answer"]


Task:
Simulate answering calls and adding new calls to queue.

5. Print Job Scheduling (Queue)

Dataset Example:

jobs = ["Doc1", "Doc2", "Doc3"]
ops = ["print", "add:Doc4", "print", "print"]


Task:
Simulate print queue and return remaining jobs.

6. Hospital ER Priority Queue

Dataset Example:

patients = [(2, "John"), (5, "Alice"), (1, "Bob")]


Task:
Serve patients based on highest priority number first.

7. CPU Job Scheduling (Priority Queue)

Dataset Example:

jobs = [(3, "Build"), (1, "Test"), (5, "Deploy")]


Task:
Return job execution order by priority.

8. Recent Browser Tabs (Stack)

Dataset Example:

actions = ["open:google.com", "open:youtube.com", "close", "open:github.com"]


Task:
Track open tabs using stack (close = pop last tab).

9. Bank Token System (Queue)

Dataset Example:

tokens = ["T1", "T2"]
ops = ["serve", "add:T3", "serve", "serve"]


Task:
Simulate serving tokens and adding new ones.

10. Airport Landing Scheduling (Priority Queue)

Dataset Example:

planes = [(3, "FlightA"), (1, "FlightB"), (4, "FlightC")]


Task:
Return landing order by priority (higher = earlier landing).