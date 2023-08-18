from flask import Flask
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
app.secret_key = ['mynameisslimshady']
CORS(app)
