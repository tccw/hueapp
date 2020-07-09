# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
from phue import Bridge
import datetime
import time
from scene_scripts.helpers import load_file

# constants
file = "/scene_scripts/data/data.txt"
path = os.getcwd() + file
sys.stdout.write(path)
data = load_file(path)
bridge_ip = data[3]
sys.stderr.write("here now")
b = Bridge(bridge_ip)  # your bridge IP here
b.connect()

lr_lamp = [1, 4]
b.set_light(lr_lamp, 'on', True)

# TODO: integrate with Celery and change to function with params (time_limit)
while True:
    bri_val_f = np.random.randint(20, 180)  # Random brightness
    t = np.random.randint(15, 500)  # Random transition time in seconds
    pchance = np.random.uniform(0, 1)  # Random number to determine the state of the lights

    tnow = datetime.datetime.now()

    if tnow.hour >= 17 or tnow.hour <= 5:  # Blue is only seen on the dark side of the earth

        if pchance < 0.1:  # set red and green
            b.set_light(lr_lamp, 'bri', bri_val_f, transitiontime=t)
            b.set_light(lr_lamp[0], 'xy', [0.3, 1.], transitiontime=t)
            b.set_light(lr_lamp[1], 'xy', [1., 0.2], transitiontime=t / 2)
            time.sleep(t / 10)
        if pchance < 0.15:  # set blueish
            b.set_light(lr_lamp, 'bri', bri_val_f, transitiontime=t)
            b.set_light(lr_lamp, 'xy', [0., 0.], transitiontime=t / 2)
            time.sleep(t / 10)
        if pchance < 0.75:  # set green
            b.set_light(lr_lamp, 'bri', bri_val_f, transitiontime=t)
            b.set_light(lr_lamp, 'xy', [0.3, 1.], transitiontime=t / 2)
            time.sleep(t / 10)
    else:

        if pchance < 0.2:  # set red and green
            b.set_light(lr_lamp, 'bri', bri_val_f, transitiontime=t)
            b.set_light(lr_lamp[0], 'xy', [0.3, 1.], transitiontime=t)
            b.set_light(lr_lamp[1], 'xy', [1., 0.2], transitiontime=t / 2)
            time.sleep(t / 10)
        if pchance < 0.8:  # set green
            b.set_light(lr_lamp, 'bri', bri_val_f, transitiontime=t)
            b.set_light(lr_lamp, 'xy', [0.3, 1.], transitiontime=t / 2)
            time.sleep(t / 10)
