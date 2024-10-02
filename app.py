from flask import Flask, request, jsonify, session
from openai import OpenAI
from decouple import config
import json
from flask_session import Session

from datetime import timedelta


openAI_key = config('OPENAI_KEY')

client = OpenAI(api_key=openAI_key)

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
