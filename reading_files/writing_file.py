# கோப்பை open பண்ணுகிறோம்
with open("yourdata.txt", "r", encoding="utf-8") as file:
    # உள்ளடக்கத்தை line by line பிரிண்ட் பண்ணுகிறோம்
    for line in file:
        print(line.strip())
