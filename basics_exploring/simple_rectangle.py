import turtle
from time import sleep

# getting ready with the pen
turtle.reset()
turtle.turtlesize(3)
turtle.pensize(3)
turtle.speed(1)
turtle.up()
sleep(2)

w = int(input("Enter width: "))
h = int(input("Enter height: "))

# name = turtle.textinput("Name Input", "What is your name?")
# num = turtle.numinput("Number Input", "Enter a number:", default=50, minval=10, maxval=200)

# Informing user what is happening
turtle.write(f"waking up", font=("Calibri", 24))
turtle.forward(-150)
turtle.down()

# Starting to draw
turtle.forward(w)
turtle.left(90)
turtle.forward(h)
turtle.left(90)
turtle.forward(w)
turtle.left(90)
turtle.forward(h)
sleep(3)