from colorama import Fore, init, Style
from PIL import Image
from typing import Tuple
import os, requests, time, math

def lat_lon_to_mercator(lat, lon, map_width, map_height) -> Tuple[int, int]:    # lat lon
    longitude_rad = lon * math.pi / 180
    latitude_rad = lat * math.pi / 180

    x_scale = map_width / 2 / math.pi
    y_scale = map_height / 2 / math.pi

    x = map_width / 2 + x_scale * longitude_rad
    y = map_height / 2 - y_scale * math.log((1 + math.sin(latitude_rad)) / (1 - math.sin(latitude_rad)))

    return int(y), int(x)
    
init(autoreset=True)
# TW
LAT = 25.02
LON = 121.52

# San Francisco
LAT = 37.7749
LON = -122.4194

# Wellington
LAT = -41.2865
LON = 174.7762

# src: https://www.joaoleitao.com/wp-content/uploads/2019/04/World-Map.jpg
img = Image.open("map.jpg")
# img = Image.open("map.gif")

width, height = img.size
ratio = height / width
new_width = 540
new_height = int(ratio * new_width * 0.45)
# new_height = 180
img = img.resize((new_width, int(new_height)))

img = img.convert('L')
pixels = img.getdata()

# Convert pixels to ascii
ascii_str = ''
for pixel_value in pixels:
    ascii_str += ' .,*aY=#+PA%BDJ@'[pixel_value // 17]  # pixel value 0-255
#  @JD%*P+#Y.

# Convert the string to a 2D array (lat, lon)
ascii_img = []  
for i in range(0, len(ascii_str), new_width):
    ascii_img.append([Fore.LIGHTGREEN_EX + char + Style.RESET_ALL for char in ascii_str[i:i+new_width]])

x, y = lat_lon_to_mercator(LAT, LON, new_width, new_height)
# x, y = new_height - int(LAT + 90 % 180), int(LON + 180 % 360)
print(LAT, LON)
print(x, y)

ascii_img[x][y] = Fore.RED + '&' + Fore.RESET


# Print the map
for row in ascii_img:
    print(''.join(row))

