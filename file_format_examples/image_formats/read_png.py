from PIL import Image
import numpy as np

img = Image.open("logo.png")
arr = np.array(img)
print("Shape:", arr.shape)  # (height, width, channels)
print(arr[:2, :2])  # top-left pixels

# Raw bytes
with open("logo.png", "rb") as f:
    print(f.read(64))
