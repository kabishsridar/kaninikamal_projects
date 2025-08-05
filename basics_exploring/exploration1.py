# print("வணக்கம் உலகம்")

print("Hello, World!")

name = "Ravi"
age = 25

print(name)
print(age)

fruits = ["apple", "banana"]

# print(fruits)

age = 10
# if age >= 18:
    # print("Eligible to vote")
# else:
    # print("Not eligible")

# for i in range(5):
#     print(i)

count = 1
while count <= 5:
    print(count)
    count += 1

colors = ["red", "green", "blue"]
print(colors[0])  # prints "red"

def greet(name):
    # print("Hello", name)
    print(f"Hello {name}")

greet("Anu")
greet("Azhagi")
greet("Arul")
greet("Murugan")

with open("hello.txt", "w") as flocation:
    flocation.write("This is written by Python.")

try:
    result = 10 / 10
except ZeroDivisionError:
    print("Cannot divide by zero!")

name = "Sara"
age = 22
print(f"{name} is {age} years old")
