import keras
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, make_response, jsonify
import tensorflow as tf
app = Flask(__name__)


class DiffSessions:
    global graph
    graph = tf.get_default_graph()
    model = keras.models.load_model('../weights/disease_predictor.h5')
    print(model.summary())
    threshold = 0.65
    current_symptoms_yes = []
    current_symptoms_no = []
    symptoms_list = pd.read_csv("../datasets/Testing.csv")
    disease_list = pd.read_csv("../datasets/Testing.csv")
    with open('SymptomsAndDiseasesList.pickle', 'wb') as f:
        symptoms_list, disease_list = pickle.load(f)
    symptom2vec = {}
    vec2symptom = {}
    all_possible_diseases = []
    all_possible_symptom = []
    number_of_top_diseases = 5
    current_disease_list = []
    symp = {}
    query = ""
    last_asked = ""
    with open('../datasets/symp.pickle', 'rb') as handle:
        symp = pickle.load(handle)


@app.route('/', methods=['POST'])
def result():
    data = request.json
    print(data)
    query = ""

    return make_response(jsonify({'fullfilmenttext':query}))