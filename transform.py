from colorama import Fore, init, Style
from PIL import Image
from typing import Tuple
import os, requests, time, math

def lat_lon_to_mercator(lat, lon, map_width, map_height) -> Tuple[int, int]:    # lat lon
    longitude_rad = lon * math.pi / 180
    latitude_rad = lat * math.pi / 180

    # calculate longitude scale, it ranges from -pi to +pi radians, so we need to / 2pi to get the scale factor ranging from 0 to 1
    x_scale = map_width / 2 / math.pi

    # Mercator projection stretches north-south, theoretically ranges from -infinity to +infinity, so we need to dynamic scale it to try to get the relative correct range from 0 to 1
    # Too far north or south and the map distorts, Google Map supports up to 85 degrees north and south
    min_lat = -85 * math.pi / 180
    max_lat = 85 * math.pi / 180

    min_mercator = math.log(math.tan((math.pi / 4) + (min_lat / 2)))
    max_mercator = math.log(math.tan((math.pi / 4) + (max_lat / 2)))

    y_scale = map_height / (max_mercator - min_mercator)
    # y_scale = map_height / 2 / math.pi

    x = map_width / 2 + x_scale * longitude_rad
    print(y_scale * (math.log(math.tan((math.pi / 4) + (latitude_rad / 2)))))
    y = map_height / 2 - y_scale * (math.log(math.tan((math.pi / 4) + (latitude_rad / 2))))
    # print(y_scale * math.log((1 + math.sin(latitude_rad)) / (1 - math.sin(latitude_rad))))
    # y = map_height / 2 - y_scale * math.log((1 + math.sin(latitude_rad)) / (1 - math.sin(latitude_rad)))
    print('y_scale: ',y_scale)

    return int(y), int(x)
    
init(autoreset=True)
# TW
LAT = 25.02
LON = 121.52

# San Francisco
# LAT = 37.7749
# LON = -122.4194

# Wellington
# LAT = -41.2865
# LON = 174.7762

# Selawik
# LAT = 66.6
# LON = -160

# Enderby Island
# LAT = -50.5
# LON = 166.3

# McMerdo Station
# LAT = -77.85
# LON = 166.6667
# LAT = 0
# LON = 0

# src: https://www.joaoleitao.com/wp-content/uploads/2019/04/World-Map.jpg
img = Image.open("MproMap.png")
# img = Image.open("map.gif")

width, height = img.size
ratio = height / width

map_width = 420
map_height = int(ratio * map_width * 0.45)
print('map size: ', map_height, map_width)
# map_height = 180
img = img.resize((map_width, int(map_height)))

img = img.convert('L')
pixels = img.getdata()

# Convert pixels to ascii
ascii_str = ''
for pixel_value in pixels:
    ascii_str += ' .,*aY=#+PA%BDJ@'[pixel_value // 17]  # pixel value 0-255
#@JDB%AP+#=Ya*,. 

# Convert the string to a 2D array (lat, lon)
ascii_img = []  
for i in range(0, len(ascii_str), map_width):
    ascii_img.append([Fore.LIGHTBLACK_EX + char + Style.RESET_ALL for char in ascii_str[i:i+map_width]])

x, y = lat_lon_to_mercator(LAT, LON, map_width, map_height)
# x, y = map_height - int(LAT + 90 % 180), int(LON + 180 % 360)
print(LAT, LON)
print(x, y)


# for i in range(-84, 85):
#     lat, lon = lat_lon_to_mercator(i, 121.5, map_width, map_height)
#     ascii_img[lat][lon] = Fore.RED + '&' + Fore.RESET
#     if i == 0:
#         ascii_img[lat][lon] = Fore.CYAN + 'X' + Fore.RESET

# ascii_img[x][y] = Fore.BLUE + '&' + Fore.RESET

# Print the map
for row in ascii_img:
    print(''.join(row))

