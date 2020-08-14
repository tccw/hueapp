from phue import Bridge
import dotenv
import os

#constants
dotenv.load_dotenv(dotenv.find_dotenv())
b = Bridge(os.getenv('BRIDGE_IP'))
b.connect()

others = [5,6,7,8]

def bedtime(p: float) -> None:
    command = {'transitiontime' : 30, 'on' : True, 'bri' : bri_pcnt(p)}
    b.set_light(others, 'on', False)

    b.set_group('Floor Lamp', command)
    b.set_group('Bedroom', command)
    

def bri_pcnt(p: float) -> int:
    if p > 1:
        return 254
    elif p < 0: 
        return 0
    else:
        return int(254 * p)


