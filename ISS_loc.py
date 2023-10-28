from PIL import Image
from colorama import Fore, init, Style
from typing import Tuple
import os, requests, time, math, copy

# https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/International_Space_Station/Where_is_the_International_Space_Station

init(autoreset=True)

img = Image.open("map.png")
width, height = img.size
ratio = height / width

MAP_Width = 1600
MAP_Height = int(ratio * MAP_Width * 0.4)

call_freq = 10 # seconds

history_queue = []
history_queue_max_size = 10800 / call_freq # 3 hrs (2 orbits), ISS orbits the Earth every 90 minutes


def lat_lon_to_mercator(lat, lon, MAP_Width, MAP_Height) -> Tuple[int, int]:    # lat lon
    longitude_radians = lon * math.pi / 180
    latitude_radians = lat * math.pi / 180

    x_scale = MAP_Width / 2 / math.pi

    # Mercator projection stretches north-south, theoretically ranges from -infinity to +infinity, so we need to dynamic scale it to try to get the relative correct range from 0 to 1
    # Too far north or south and the map distorts, Google Map supports up to 85 degrees north and south
    # min_lat = -85 * math.pi / 180
    # max_lat = 85 * math.pi / 180

    # min_mercator = math.log(math.tan((math.pi / 4) + (min_lat / 2)))
    # max_mercator = math.log(math.tan((math.pi / 4) + (max_lat / 2)))

    # y_scale = MAP_Height / (max_mercator - min_mercator)
    y_scale = MAP_Height / 2 / math.pi

    x = MAP_Width / 2 + x_scale * longitude_radians
    
    # y = MAP_Height / 2 - y_scale * (math.log(math.tan((math.pi / 4) + (latitude_radians / 2))))
    y = MAP_Height / 2 - y_scale * math.log((1 + math.sin(latitude_radians)) / (1 - math.sin(latitude_radians)))
    
    return int(y), int(x)

def ISS_loc(lat: float, lon: float) -> list:
    if MAP_Width <= 200:
        side = 0
    elif MAP_Width <= 540:
        side = 1
    else:
        side = 2

    loc = []
    for i in range(-side, side+1):
        if  lat+i >= 0 and lat+i < MAP_Height and lon+i >= 0 and lon+i < MAP_Width:            
            loc.append([lat-i, lon+i, '*'])
            loc.append([lat-i, lon-i, '*'])
            loc.append([lat+i, lon, '*'])
            loc.append([lat, lon+i, '*'])
    return loc


img = img.resize((MAP_Width, int(MAP_Height)))
img = img.convert('L') # grey scale
pixels = img.getdata()

ascii_str = ''
for pixel_value in pixels:
    ascii_str += ' .,*aY=#+PA%BDJ@'[pixel_value // 17]  # pixel value 0-255
#@JDB%AP+#=Ya*,. 

# Convert the string to a 2D array (lat, lon)
ascii_img = []  
for i in range(0, len(ascii_str), MAP_Width):
    ascii_img.append([char for char in ascii_str[i:i+MAP_Width]])

ascii_backup = copy.deepcopy(ascii_img)


url = 'http://api.open-notify.org/iss-now.json'

while True:
    os.system("cls")

    try:
        response = requests.get(url).json() 
    except Exception as e:
        print(e)
        time.sleep(10)
        continue

    LAT = float(response['iss_position']['latitude'])
    LON = float(response['iss_position']['longitude'])

    x, y = lat_lon_to_mercator(LAT, LON, MAP_Width, MAP_Height)
    # x, y = MAP_Height - int(LAT + 90 % 180), int(LON + 180 % 360)
    print(LAT, LON)
    print(x, y)
    print('Map size: ', MAP_Width, MAP_Height)

    history_queue.insert(0, [x, y])
    
    if len(history_queue) > history_queue_max_size:
        pop_loc = history_queue.pop()
        ascii_img[pop_loc[0]][pop_loc[1]] = Style.RESET_ALL + ascii_backup[pop_loc[0]][pop_loc[1]]

    # Draw 2hr history
    for idx, h in enumerate(history_queue):
        # if first half, be cyan, else yellow
        if idx < history_queue_max_size // 2:
            ascii_img[h[0]][h[1]] = Fore.CYAN + '>' + Fore.RESET
        else:
            ascii_img[h[0]][h[1]] = Fore.YELLOW + '>' + Fore.RESET

    # ascii_img[x][y] = Fore.RED + '&' + Fore.RESET

    # Draw ISS location
    for loc in ISS_loc(x, y):
        try:
            ascii_img[loc[0]][loc[1]] = Fore.LIGHTYELLOW_EX + loc[2] + Fore.RESET
        except:
            pass

    for row in ascii_img:
        print(''.join(row))
        
    # restore the map
    for loc in ISS_loc(x, y):
        ascii_img[loc[0]][loc[1]] =  Style.RESET_ALL + ascii_backup[loc[0]][loc[1]]

    time.sleep(call_freq)