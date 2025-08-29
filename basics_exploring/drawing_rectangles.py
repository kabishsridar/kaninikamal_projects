import sys
import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel

rectangles = []
console = Console()

# Case 1: argv
if len(sys.argv) == 3:
    w, h = map(int, sys.argv[1:3])
    rectangles.append((w, h))

# Case 2: stdin, another CLI option
elif not sys.stdin.isatty():
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) == 2:
            w, h = map(int, parts)
            rectangles.append((w, h))

elif len(sys.argv) == 2:
    print("You must have given a file.csv \n")
    with open(sys.argv[1], "r") as fdata:
        # read each line of the file
        for line in fdata.readlines()[1:]:
            line = line.strip()
            w, h = line.split(",")
            rectangles.append((int(w), int(h)))

# Case 3: interactive
else:
    w = int(input("Enter width: "))
    h = int(input("Enter height: "))
    rectangles.append((w, h))

def draw_rect(w, h):
    text = ("\n".join([" " * w for _ in range(h)])) or " "
    panel = Panel(text, title=f"{w}x{h}", border_style="blue")
    console.print(panel)

def draw_square(size, color="cyan"):
    for _ in range(size):
        console.print("█ " * size, style=color)

# draw_square(w)
# drawing ascii or rich console doesn't work as expected.
# There is no direct work around in python

# Draw them in Maptplotlib

fig, ax = plt.subplots()
x, y = 0, 0  # start position
for w, h in rectangles:
    rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor="blue", linewidth=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, f"{w}x{h}", ha="center", va="center")
    x += w + 5  # shift next rectangle to the right

ax.set_aspect("equal")
ax.set_xlim(0, sum(w for w, _ in rectangles) + 20)
ax.set_ylim(0, max(h for _, h in rectangles) + 20)
plt.show()
plt.savefig("rectangle.png", transparent=True)