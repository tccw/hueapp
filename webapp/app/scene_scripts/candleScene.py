"""
A better candle scene
"""
import os
import numpy as np
from phue import Bridge
from math import ceil
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
b.set_light(lr_lamp, 'ct', 380, transitiontime=0)  # set color temp.

m = 2  # brightness multiplier

while True:

    pchance = np.random.uniform(0, 1)

    if pchance <= 0.001:  # 0.1 percent chance of gusty breeze
        n = 0
        n_flickers = np.random.randint(2, 6)

        while n < n_flickers:  # simulate disturbed air around a candle
            t0 = np.random.randint(0.5, 2)
            t1 = np.random.randint(0.5, 2)
            bri_val_f0 = np.random.randint(60, 110)
            bri_val_f1 = np.random.randint(60, 120)

            b.set_light(lr_lamp[0], 'bri', ceil(bri_val_f0 * m), transitiontime=t0)
            b.set_light(lr_lamp[1], 'bri', ceil(bri_val_f1 * m), transitiontime=t1)

            n = n + 1
    else:
        t0 = np.random.randint(3, 8)
        t1 = np.random.randint(3, 8)
        bri_val_f0 = np.random.randint(90, 100)
        bri_val_f1 = np.random.randint(90, 100)

        b.set_light(lr_lamp[0], 'bri', ceil(bri_val_f0 * m), transitiontime=t0)
        b.set_light(lr_lamp[1], 'bri', ceil(bri_val_f1 * m), transitiontime=t1)
