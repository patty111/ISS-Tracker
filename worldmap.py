import PIL.Image
from colorama import Fore, init
import os, requests, time, math

# https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/International_Space_Station/Where_is_the_International_Space_Station

def lat_lon_to_mercator(lat, lon, map_width, map_height):
    # TODO: Function Incorrect
    x = (lon + 180) * (map_width / 360)

    # convert from degrees to radians
    lat_rad = lat * math.pi / 180

    # mercator projection
    merc_n = math.log(math.tan((math.pi / 4) + (lat_rad / 2)))
    y = (map_height / 2) - (map_width * merc_n / (2 * math.pi))

    return int(x), int(y)

init(autoreset=True)

history_queue = []
history_queue_size = 1800 # 3 hrs, ISS orbits Earth every 90 minutes

img_flag = True
path = "map.gif"
# path = "world_map.png"

try:
    img = PIL.Image.open(path)
    img_flag = True
except:
    print(path, "Unable to find image ");

width, height = img.size
ratio = height / width

new_width = 324
new_height = int(ratio * new_width * 0.55)

img = img.resize((new_width, int(new_height)))
img = img.convert('L')

# chars = "@JD%*P.Y +#"
chars = " @JD%*P+#Y."

pixels = img.getdata()

new_pixels = [chars[pixel//25] for pixel in pixels]
new_pixels = ''.join(new_pixels)
new_pixels_count = len(new_pixels)

ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
ascii_image = "\n".join(ascii_image)

url = 'http://api.open-notify.org/iss-now.json'

while True:
    os.system("cls")

    response = requests.get(url).json() 
    lat = float(response['iss_position']['latitude'])
    lon = float(response['iss_position']['longitude'])
    # print(response)

    # rel_coord = [int((90 + lat) / 180 * new_height), int((lon + 180) / 360 * new_width)]
    x, y = lat_lon_to_mercator(lat, lon, new_width, new_height)
    rel_pos = y * new_width + x
    # rel_pos = (new_height - rel_coord[0]) * new_width + rel_coord[1]
    print('latitude and longitude: ', lat, lon, 'perct: ', (90 + lat) / 180 * 100, '%  ' , (lon + 180) / 360 * 100, '%')
    # print('relative coordinate: ', rel_coord, ' perct: ', rel_coord[0] / new_height * 100, '%  ', rel_coord[1] / new_width * 100, '%')

    print('relative position: ', rel_pos)

    history_queue.insert(0, rel_pos)
    if len(history_queue) > history_queue_size:
        history_queue.pop()

    flag = 0
    for idx, c in enumerate(ascii_image):
        if idx == rel_pos:
            print(Fore.YELLOW + '@', end="")
            flag = 1
        if idx in history_queue and flag == 0:
            print(Fore.BLUE + '%', end="")
            flag = 1
        if flag == 1:
            flag = 0
            continue

        if c == "+" or c == "Y":
            print(Fore.RED + c, end="")
        elif c == "#":
            print(Fore.LIGHTBLACK_EX + c, end="")
        else:
            print(Fore.WHITE + c, end="")
    # time.sleep(6)
    time.sleep(10)