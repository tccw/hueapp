import os
import numpy as np
from phue import Bridge
from math import floor
from scene_scripts.helpers import load_file

# constants
file = "/scene_scripts/data/data.txt"
path = os.getcwd() + file
data = load_file(path)
bridge_ip = data[3]

b = Bridge(bridge_ip)  # your bridge IP here
b.connect()

lr_lamp = [1, 4]
b.set_light(lr_lamp, 'on', True)
b.set_light(lr_lamp[0], 'xy', [0.3, 1.])
b.set_light(lr_lamp[1], 'xy', [1., 0.2])
x = np.pi
step = 0.01

while True:
    x = x + step
    bri_val = np.power(2, np.cos(x) + 1) * 50
    b.set_light(lr_lamp, 'bri', floor(bri_val), transitiontime=1)
