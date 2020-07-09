#!/usr/bin/env python3.6

from datetime import datetime
from flask import Flask, render_template, request
import sys
import os
import dotenv
from scene_scripts import auroraBorealis

dotenv.load_dotenv(dotenv.find_dotenv())

buswatch = os.getenv('BUSWATCH_CODE')
aurora = os.getenv('AURORA_CODE')

empty_response = ('', 204)
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


# ifttt trigger logic
@app.route("/ifttt-trigger", methods=['GET', 'POST'])
def start_bus_watch():
    if request.content_length is None:
        return empty_response
    elif request.content_length < 1e4:
        message = request.get_data(as_text=True)

    if message == buswatch:
        # import and immediately run busIndicator.py
        console_logger(message.lower())
        try:
            from scene_scripts import busIndicator
        except Exception as e:
            return str(e) + sys.version + "Path to python: " + sys.executable 
        return "buswatch"
    elif message == aurora:
        try:
            auroraBorealis.aurora(2)
            return ("ran and terminated", 200)
        except Exception as e:
            return str(e) + sys.version + "Path to python: " + str(sys.path)
    return empty_response

def console_logger(module):
    print("Log {}: running {}".format(datetime.now(), module))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
