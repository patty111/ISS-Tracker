from PIL import Image
from colorama import Fore, init, Style
from typing import Tuple
import os, requests, time, math, copy

# https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/International_Space_Station/Where_is_the_International_Space_Station

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

    # y_scale = map_height / (max_mercator - min_mercator)
    y_scale = map_height / 2 / math.pi

    x = map_width / 2 + x_scale * longitude_rad
    
    # y = map_height / 2 - y_scale * (math.log(math.tan((math.pi / 4) + (latitude_rad / 2))))
    y = map_height / 2 - y_scale * math.log((1 + math.sin(latitude_rad)) / (1 - math.sin(latitude_rad)))
    
    # print('y_scale: ',y_scale)

    return int(y), int(x)

def ISS_loc(lat: float, lon: float) -> list:
    if map_width < 540:
        radius = 1
    else:
        radius = 2

    aspect_ratio = 2
    loc = []
    for i in range(-radius, radius+1):
        for j in range(-radius, radius+1):
            if  lat+i >= 0 and lat+i < map_height and lon+j >= 0 and lon+j < map_width:
                if (i / aspect_ratio)**2 + j**2 <= radius**2:
                    loc.append([lat+i, lon+j, '*'])
                else:
                    loc.append([lat+i, lon+j, ' '])
            else:
                continue
    return loc

init(autoreset=True)

history_queue = []
history_queue_max_size = 1080 # 3 hrs (2 orbits), ISS orbits the Earth every 90 minutes

# src: https://www.joaoleitao.com/wp-content/uploads/2019/04/World-Map.jpg
img = Image.open("map.png")

width, height = img.size
ratio = height / width

map_width = 1560
map_height = int(ratio * map_width * 0.38)

img = img.resize((map_width, int(map_height)))
img = img.convert('L') # grey scale
pixels = img.getdata()

ascii_str = ''
for pixel_value in pixels:
    ascii_str += ' .,*aY=#+PA%BDJ@'[pixel_value // 17]  # pixel value 0-255
#@JDB%AP+#=Ya*,. 

# Convert the string to a 2D array (lat, lon)
ascii_img = []  
for i in range(0, len(ascii_str), map_width):
    ascii_img.append([char for char in ascii_str[i:i+map_width]])

ascii_backup = copy.deepcopy(ascii_img)


url = 'http://api.open-notify.org/iss-now.json'

while True:
    os.system("cls")

    response = requests.get(url).json() 
    LAT = float(response['iss_position']['latitude'])
    LON = float(response['iss_position']['longitude'])

    x, y = lat_lon_to_mercator(LAT, LON, map_width, map_height)
    # x, y = map_height - int(LAT + 90 % 180), int(LON + 180 % 360)
    print(LAT, LON)
    print(x, y)
    print('Map size: ', map_width, map_height)

    history_queue.insert(0, [x, y])
    
    if len(history_queue) > history_queue_max_size:
        pop_loc = history_queue.pop()
        ascii_img[pop_loc[0]][pop_loc[1]] = Style.RESET_ALL + ascii_backup[pop_loc[0]][pop_loc[1]]

    # if len(history_queue) > 1 and history_queue[0] != history_queue[1]:
    #     ascii_img[history_queue[1][0]][history_queue[1][1]] = Fore.CYAN + '>' + Fore.RESET
    # Draw 2hr history
    for idx, h in enumerate(history_queue):
        # if first half, be cyan, else yellow
        if idx < history_queue_max_size // 2:
            ascii_img[h[0]][h[1]] = Fore.CYAN + '>' + Fore.RESET
        else:
            ascii_img[h[0]][h[1]] = Fore.YELLOW + '>' + Fore.RESET

    ascii_img[x][y] = Fore.RED + '&' + Fore.RESET

    # Draw ISS location
    for loc in ISS_loc(x, y):
        ascii_img[loc[0]][loc[1]] = Fore.RED + loc[2] + Fore.RESET


    for row in ascii_img:
        print(''.join(row))
        
    # restore the map
    for loc in ISS_loc(x, y):
        ascii_img[loc[0]][loc[1]] =  Style.RESET_ALL + ascii_backup[loc[0]][loc[1]]
    time.sleep(10)