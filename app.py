# app.py
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Python App v1.0!\n"

if __name__ == '__main_':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))