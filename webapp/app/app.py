#!/usr/bin/env python3.6

from datetime import datetime
from flask import Flask, render_template, request
import os
import sys
#from dotenv import load_dotenv, find_dotenv
from scene_scripts import auroraBorealis

#load_dotenv(find_dotenv())

#buswatch = os.environ.get("BUSWATCH_CODE")
#aurora = os.environ.get("AURORA_CODE")
buswatch = ""
aurora = "AURORA-ca51142d-ce65-4c08-96d3-90cc5f7d12d0"
empty_response = ('', 204)
OK_response = ('', 200)
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


# ifttt trigger logic
@app.route("/ifttt-trigger", methods=['GET', 'POST'])
def start_bus_watch():
    if request.content_length is None:
        return ('Lenght is NONE', 204)
    elif request.content_length < 1e4:
        message = request.get_data(as_text=True)

    if message == buswatch:
        try:
            from scene_scripts import busIndicator
            aurora
        except Exception as e:
            return str(e) + sys.version + "Path to python: " + sys.executable 
        return "buswatch"
    elif message == aurora:
        try:
            auroraBorealis.aurora(20)
            return OK_response 
        except Exception as e:
            return str(e) + sys.version + "Path to python: " + str(sys.path)
    return ('No body in POST', 204)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
