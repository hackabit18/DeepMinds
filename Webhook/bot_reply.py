import keras
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, make_response, jsonify
import tensorflow as tf
app = Flask(__name__)


@app.route('/', methods=['POST'])
def result():
    data = request.json

    query = ""

    return make_response(jsonify({'fullfilmenttext':query}))