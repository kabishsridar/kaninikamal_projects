import turtle
import sys
import csv

# Setup turtle
turtle.speed(2)       # medium speed
turtle.turtlesize(2)  # bigger turtle
turtle.pensize(4)     # thicker pen

def draw_rectangle(w, h):
    for _ in range(2):
        turtle.forward(w)
        turtle.left(90)
        turtle.forward(h)
        turtle.left(90)

# ---- Input method selection ----
if len(sys.argv) == 1:
    # Case 1: Interactive CLI input()
    w = int(input("Enter width: "))
    h = int(input("Enter height: "))
    draw_rectangle(w, h)
    turtle.up()
    turtle.backward(100)
    turtle.write("Done", font=("Calibri", 20))
    turtle.done()

elif len(sys.argv) == 3:
    # Case 2: CLI arguments (argv)
    w = int(sys.argv[1])
    h = int(sys.argv[2])
    draw_rectangle(w, h)
    turtle.up()
    turtle.backward(100)
    turtle.write("Done", font=("Calibri", 20))
    turtle.done()

elif len(sys.argv) == 2:
    # Case 3: CSV input
    csv_file = sys.argv[1]
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        colors = ["red", "blue", "green", "purple", "orange"]
        for i, row in enumerate(reader):
            w = int(row["width"])
            h = int(row["height"])
            turtle.pencolor(colors[i % len(colors)])  # different color per rect
            draw_rectangle(w, h)
            turtle.penup()
            turtle.left(90)
            turtle.forward(100)  # space before next rect
            turtle.pendown()
    turtle.up()
    turtle.forward(100)
    turtle.write("Done", font=("Calibri", 20))
    turtle.done()

else:
    print("Usage:")
    print("  python rect.py            # interactive input")
    print("  python rect.py <w> <h>    # argv input")
    print("  python rect.py file.csv   # csv input")
    sys.exit(1)

turtle.done()