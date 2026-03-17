from PIL import Image
import os

path = r'c:\Milton\keep_driving\assets\sprites\desert_road_3.png'
if os.path.exists(path):
    img = Image.open(path).convert("RGBA")
    alpha_data = list(img.getchannel("A").getdata())
    total_alpha = sum(alpha_data)
    print(f"File: {path}")
    print(f"Size: {img.size}")
    print(f"Total Alpha: {total_alpha}")
    print(f"Max Alpha: {max(alpha_data)}")
else:
    print("File not found")
