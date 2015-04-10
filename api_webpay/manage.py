# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.script import Manager, Server
from __init__ import app
from utils import initial
import os

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = app.config['DEBUG'],
    use_reloader = app.config['RELOAD'],
    host = app.config['HOST'],
    port = app.config['PORT'],)
)

os.environ['TBK_COMMERCE_ID'] = app.config['COMMERCE_ID']
os.environ['TBK_COMMERCE_KEY'] = app.config['COMMERCE_KEY']

def register_blueprints(app):
    import webpay
    webpay.initialize_app(app)


register_blueprints(app)

if __name__ == "__main__":

    initial()
    manager.run()
