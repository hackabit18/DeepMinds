import pickle
import keras
import numpy as np
import tensorflow as tf
import pandas as pd
from flask import Flask, request, make_response, jsonify
from collections import OrderedDict
app = Flask(__name__)

with open('../model/SymptomsAndDiseasesList.pickle', 'rb') as f:
    _, disease_list = pickle.load(f)

symptoms_list = np.array(pd.read_csv('../datasets/Training.csv').columns.values)[:-1]
# for i in range(len(symptoms_list)):
#     symptoms_list[i] = symptoms_list[i].replace('_', ' ')

with open('../datasets/DiseaseToSymptomsDictionary.pickle', 'rb') as handle:
    symp = pickle.load(handle)


class DiffSessions:
    global symptoms_list, symp
    graph = tf.get_default_graph()
    model = keras.models.load_model('../model/DiseasePredictor.h5')
    print(model.summary())
    threshold = 0.65
    current_symptoms_yes = []
    current_symptoms_no = []

    symptom2vec = {}
    vec2symptom = {}
    all_possible_diseases = []
    all_possible_symptom = []
    number_of_top_diseases = 5
    current_disease_list = []
    query = ""
    last_asked = ""
    thres = 4
    new_map = {}
    current_disease_list_local = []
    c = 0

    for i in range(len(symptoms_list)):
        symptom2vec[symptoms_list[i]] = i
        vec2symptom[i] = symptoms_list[i]

    def getListOfSymptoms(self, one_hot):
        symptoms_return = []
        for iterate in range(len(one_hot)):
            if one_hot[iterate] == 1:
                symptoms_return.append([symptoms_list[iterate]])

        return symptoms_return

    def getOneHot(self, symptoms):
        # print(symptoms)
        one_hot = []
        for i in range(len(symptoms_list)):
            # print(symptoms_list[i])
            if symptoms_list[i] in symptoms:
                one_hot.append(1)
            else:
                one_hot.append(0)

        return one_hot

    def addToSymptomsList(self, symptoms_yes, symptoms_no):
        print(symptoms_yes, symptoms_no)
        for items in symptoms_yes:
            if items not in self.current_symptoms_yes:
                self.current_symptoms_yes.append(items)
        for items in symptoms_no:
            if items not in self.current_symptoms_no:
                self.current_symptoms_no.append(items)

    def get_result(self, data):
        if 'action' not in data['queryResult']:
            self.addToSymptomsList(data['queryResult']['parameters']['medical'], [])
            self.getPrediction()
            self.last_asked, self.query = self.ask_question()
            print(self.last_asked, self.query)

        else:
            print(data['queryResult']['action'])
            if data['queryResult']['action'] == "MedicalConversation.MedicalConversation-yes":
                print("Yassss")
                self.current_symptoms_yes.append(self.last_asked)
            if data['queryResult']['action'] == "MedicalConversation.MedicalConversation-no":
                print("Noooo")
                self.current_symptoms_no.append(self.last_asked)

            print(data['queryResult']['action'])
            print(self.current_symptoms_yes)
            print(self.current_symptoms_no)

            self.last_asked, self.query = self.ask_question()

        return self.last_asked, self.query

        # if data['queryResult']['action'] == "MedicalConversation.MedicalConversation-yes":
        #     current_symptoms_yes.append(self.last_asked)
        # if data['queryResult']['action'] == "MedicalConversation.MedicalConversation-no":
        #     current_symptoms_no.append(self.last_asked)
        # symptoms = data['queryResult']['parameters']['medical']
        # addToSymptomsList(symptoms, [])

    def getPrediction(self):
        self.c = 0
        # print(symptoms_list, "---------")
        # print(self.current_symptoms_yes)
        inputs = np.array(self.getOneHot(self.current_symptoms_yes)).reshape(-1, 132).astype('float32')
        print(inputs)
        with self.graph.as_default():
            pred = self.model.predict(inputs, batch_size=64)

        # if max(pred.all()) >= threshold:
        # print(pred.shape)
        for iterate in range(len(pred[0])):
            self.new_map[pred[0][iterate]] = disease_list[iterate]

        # print(self.new_map)
        for key in sorted(self.new_map.keys(), reverse=True):
            # print("74982738497")
            if self.new_map[key] not in self.current_disease_list:
                self.current_disease_list.append(self.new_map[key])
                print(key, self.new_map[key], "--")
                # all_possible_symptoms.append(self.new_map[key])
                self.c += 1
            if self.c > self.number_of_top_diseases:
                break

        print(self.current_disease_list, "---")

    def ask_question(self):
        # global self.current_disease_list, self.current_symptoms_yes, self.current_symptoms_no, symp
        x = len(self.current_symptoms_yes)
        while x < self.thres:
            for i in self.current_disease_list:
                print(symp[i], "-----")
                for j in symp[i]:

                    if (j in self.current_symptoms_yes) or (j in self.current_symptoms_no):
                        continue
                    else:
                        # x += 1
                        ask = "Do you also have " + j.replace("_", " ") + "?"
                        print(j, ask)
                        return j, ask

        else:
            # dise =
            # print(self.current_symptoms_yes)
            inputs = np.array(self.getOneHot(self.current_symptoms_yes)).reshape(-1, 132).astype('float32')
            # print(inputs)
            with self.graph.as_default():
                pred = self.model.predict(inputs, batch_size=64)

            # if max(pred.all()) >= threshold:
            # print(pred.shape)
            self.new_map = {}
            for iterate in range(len(pred[0])):
                self.new_map[pred[0][iterate]] = disease_list[iterate]

            # print(self.new_map)
            for key in sorted(self.new_map.keys(), reverse=True):
                # print("74982738497")
                if self.new_map[key] not in self.current_disease_list_local:
                    self.current_disease_list_local.append(self.new_map[key])
                print(key, self.new_map[key])
                # all_possible_symptoms.append(self.new_map[key])
                self.c += 1
                if self.c == 1:
                    break
            return "done", "You maybe suffering from " + self.current_disease_list_local[0] + "."

            # receive =

            # ask = "Do you also have "+
            # make_response(jsonify({'fulfillmentText': ans}))


object_dict = {}
object_list = []
iterator = 0


@app.route('/', methods=['POST'])
def result():
    global iterator

    data = request.json
    # print(data)
    # print(current_symptoms_yes)
    # print(current_symptoms_no)
    # print(query)
    # print(self.last_asked)
    obj_name = data['session']

    print(data)
    print(obj_name)

    if obj_name not in object_dict.keys():
        object_dict[obj_name] = iterator
        iterator += 1
        object_list.append(DiffSessions())

    exit_or_not, reply = object_list[object_dict[obj_name]].get_result(data)

    reply = reply.replace("_", " ")
    dictionary = {'fulfillmentText': reply}
    # print(data['queryResult']['outputContexts']['lifespanCount'])
    # dictionary['outputContexts'] = data['queryResult']['outputContexts']
    print(len(object_list))

    if exit_or_not == "exit":
        object_dict[obj_name] = iterator
        iterator += 1

    return make_response(jsonify(dictionary))


if __name__ == "__main__":
    app.run()
