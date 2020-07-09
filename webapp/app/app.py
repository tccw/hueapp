#!/usr/bin/env python3.6

from datetime import datetime
from flask import Flask, render_template, request
import sys

buswatch = "BUSWATCH-b72f6d14-69f1-408c-b2a1-c25c50bdd1d5"
aurora = "AURORA-fd2b5e7a-7c1a-4feb-a1e5-c45adb7b1723"
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
        # import and immediately run auroraBorealis.py
        console_logger(message.lower())
        try:
            from scene_scripts import auroraBorealis
            return "ran and terminated"
            #exec(open("./scene_scripts/auroraBorealis.py").read())
        except Exception as e:
            return str(e) + sys.version + "Path to python: " + str(sys.path)
        return "aurora" 
    return empty_response

def console_logger(module):
    print("Log {}: running {}".format(datetime.now(), module))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
