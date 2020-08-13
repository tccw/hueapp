# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
from phue import Bridge
from datetime import datetime, timedelta
import time
import dotenv

# constants
dotenv.load_dotenv(dotenv.find_dotenv())
b = Bridge(os.getenv('BRIDGE_IP'))  # your bridge IP here
b.connect()

lr_lamp = [1, 4]
b.set_light(lr_lamp, 'on', True)

# TODO: integrate with Celery and change to function with params (time_limit)
def aurora(runtime_sec):
    stop_time = datetime.now() + timedelta(seconds=runtime_sec)
    while stop_time > datetime.now():
        bri_val_f = np.random.randint(20, 180)  # Random brightness
        t = np.random.randint(15, 500)  # Random transition time in seconds
        pchance = np.random.uniform(0, 1)  # Random number to determine the state of the lights

        tnow = datetime.now()

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

