from PIL import Image
import numpy as np

img = Image.open("logo.jpg")
arr = np.array(img)
print("Shape:", arr.shape)

with open("logo.jpg", "rb") as f:
    print(f.read(64))