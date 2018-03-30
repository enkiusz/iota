#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import gevent
from functools import wraps
from flask import Flask
from flask_sockets import Sockets
import psycopg2

app = Flask(__name__)

admin = {
    'identity': os.environ.get('ADMIN_IDENTITY'),
    'secret': os.environ.get('ADMIN_SECRET')
}

db = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.authorization and request.authorization.username != admin['identity'] and request.authorization.password != admin['secret']:
            return "authentication required"
        return f(*args, **kwargs)
    return decorated

sockets = Sockets(app)

@app.route('/')
def hello():
    return "iota"

@app.route("/devices", methods=["GET"])
@auth_required
def devices():
    return "{ devices }"

@sockets.route('/')
def inbox(ws):

    while not ws.closed:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        print("Slept")
        message = ws.receive()
        print("msg {}".format(message))

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

