#!/usr/bin/env python3.6

from datetime import datetime
from flask import Flask, render_template, request
from celery.contrib.abortable import AbortableTask 
import sys
import os
import dotenv
from scene_scripts import Bedtime
from scene_scripts import auroraBorealis
import tasks

dotenv.load_dotenv(dotenv.find_dotenv())

buswatch = os.getenv('BUSWATCH_CODE')
aurora = os.getenv('AURORA_CODE')
bedtime = os.getenv('BEDTIME')

empty_response = ('', 204)
compl_response = ('Completed', 200)
inprog_response = ('Task in progress', 202)
no_such_cmd_response = ('No such command', 400)
app = Flask(__name__)
app.config.update(
        CELERY_BROKER_URL=os.getenv('BROKER_URL'),
        CELERY_RESULT_BACKEND=os.getenv('RESULT_BACKEND')
        )
celery = tasks.make_celery(app)

@app.route("/")
def index():
    return render_template('index.html')


# ifttt trigger logic
@app.route("/ifttt-trigger", methods=['GET', 'POST'])
def ifttt_trigger():
    if request.content_length is None:
        return empty_response
    elif request.content_length < 1e4:
        message = request.get_data(as_text=True)

    if message == buswatch:
        # import and immediately run busIndicator.py
        try:
            #from scene_scripts import busIndicator
            sys.stdout.write("Ya triggered me!")
            return inprog_response
        except Exception as e:
            return error_helper(e) 
    elif message == aurora:
        try:
            aurora_run.delay(500) # asyc call managed with celery and redis 
            return inprog_response
        except Exception as e:
            return error_helper(e)
    elif message == bedtime:
        try:
            bedtime_run(0.3)
        except Exception as e:
            return error_helper(e)
    return no_such_cmd_response

def error_helper(e):
    return str(e) + sys.version + "Path to python: " + str(sys.path)

# @celery.task allows celery to run this asynchronously
# requires a celery worker which can be started by navigating to hueapp/webapp/app 
# and running celery -A app.celery worker
# redis server must also be running which can be started with sudo /etc/init.d/redis_$PORT start
# flask.palletsprojects.com/en/1.1.x/patterns/celery
# redis.io/topics/quickstart
# TODO make sure that $REDIS_PORT is firewalled from the external net
@celery.task
def aurora_run(seconds: int) -> None:
    auroraBorealis.aurora(seconds)

@celery.task
def bedtime_run(p: int) -> None:
    Bedtime.bedtime(p)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=os.getenv('FLASK_PORT'))
