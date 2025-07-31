# Open the file and read lines
with open("yourdata.txt", "r") as file:
    lines = file.readlines()

print(lines, "Printing the lines")

# Process each line
# print("Students who scored more than 80:")
for line in lines:
    name, score_str = line.strip().split(",")
    score = int(score_str)

    if score > 80:
        print(f"{name} scored {score}")