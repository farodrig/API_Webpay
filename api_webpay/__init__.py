from flask import Flask
from flask.ext.mongoengine import MongoEngine
import os, sys

app = Flask(__name__)

config = os.path.join(app.root_path, 'config.ini')
if not os.path.exists(config):
    raise Exception("Falta el archivo config.ini")
app.config.from_pyfile(config)

app.config['MONGODB_SETTINGS'] = {
    'db': app.config['MONGO_DB'],
    'host': app.config['MONGO_HOST'],
    'port': app.config['MONGO_PORT'],
    'username': app.config['MONGO_USER'],
    'password': app.config['MONGO_PASS'],
}

db = MongoEngine(app)

if __name__ == '__main__':
    app.run()