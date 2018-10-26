import pickle
import keras
import numpy as np
import tensorflow as tf
import pandas as pd
from flask import Flask, request, make_response, jsonify
from collections import OrderedDict
# from . import send_loc
from uuid import uuid4 as places_autocomplete_session_token
from googlemaps import convert
import requests

app = Flask(__name__)

with open('../model/SymptomsAndDiseasesList.pickle', 'rb') as f:
    _, disease_list = pickle.load(f)

symptoms_list = np.array(pd.read_csv('../datasets/Training.csv').columns.values)[:-1]
for i in range(len(symptoms_list)):
    symptoms_list[i] = symptoms_list[i].replace('_', ' ')

with open('../datasets/DiseaseToSymptomsDictionary.pickle', 'rb') as handle:
    symp = pickle.load(handle)

for key, value in symp.items():
    for i in range(len(symp[key])):
        symp[key][i] = symp[key][i].replace("_", " ")


PLACES_FIND_FIELDS_BASIC = set([
    "formatted_address", "geometry", "icon", "id", "name",
    "permanently_closed", "photos", "place_id", "plus_code", "scope",
    "types",
])

PLACES_FIND_FIELDS_CONTACT = set(["opening_hours", ])

PLACES_FIND_FIELDS_ATMOSPHERE = set(["price_level", "rating"])

PLACES_FIND_FIELDS = (PLACES_FIND_FIELDS_BASIC ^
                      PLACES_FIND_FIELDS_CONTACT ^
                      PLACES_FIND_FIELDS_ATMOSPHERE)

PLACES_DETAIL_FIELDS_BASIC = set([
    "address_component", "adr_address", "alt_id", "formatted_address",
    "geometry", "icon", "id", "name", "permanently_closed", "photo",
    "place_id", "plus_code", "scope", "type", "url", "utc_offset", "vicinity",
])

PLACES_DETAIL_FIELDS_CONTACT = set([
    "formatted_phone_number", "international_phone_number", "opening_hours",
    "website",
])

PLACES_DETAIL_FIELDS_ATMOSPHERE = set(["price_level", "rating", "review", ])

PLACES_DETAIL_FIELDS = (PLACES_DETAIL_FIELDS_BASIC ^
                        PLACES_DETAIL_FIELDS_CONTACT ^
                        PLACES_DETAIL_FIELDS_ATMOSPHERE)

my_api_key = "AIzaSyDPg23pWoQC6bzMh0g5P37XUKyPdih_jXI"


def find_place(input, input_type, fields=None, location_bias=None,
               language="English"):
    """
    A Find Place request takes a text input, and returns a place.
    The text input can be any kind of Places data, for example,
    a name, address, or phone number.
    :param input: The text input specifying which place to search for (for
                  example, a name, address, or phone number).
    :type input: string
    :param input_type: The type of input. This can be one of either 'textquery'
                  or 'phonenumber'.
    :type input_type: string
    :param fields: The fields specifying the types of place data to return,
                   separated by a comma. For full details see:
                   https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type input: list
    :param location_bias: Prefer results in a specified area, by specifying
                          either a radius plus lat/lng, or two lat/lng pairs
                          representing the points of a rectangle. See:
                          https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type location_bias: string
    :param language: The language in which to return results.
    :type langauge: string
    :rtype: result dict with the following keys:
            status: status code
            candidates: list of places
    """
    params = {"input": input, "inputtype": input_type}

    if input_type != "textquery" and input_type != "phonenumber":
        raise ValueError("Valid values for the `input_type` param for "
                         "`find_place` are 'textquery' or 'phonenumber', "
                         "the given value is invalid: '%s'" % input_type)

    if fields:
        invalid_fields = set(fields) - PLACES_FIND_FIELDS
        if invalid_fields:
            raise ValueError("Valid values for the `fields` param for "
                             "`find_place` are '%s', these given field(s) "
                             "are invalid: '%s'" % (
                                 "', '".join(PLACES_FIND_FIELDS),
                                 "', '".join(invalid_fields)))
        params["fields"] = convert.join_list(",", fields)

    if location_bias:
        valid = ["ipbias", "point", "circle", "rectangle"]
        if location_bias.split(":")[0] not in valid:
            raise ValueError("location_bias should be prefixed with one of: %s"
                             % valid)
        params["locationbias"] = location_bias
    if language:
        params["language"] = language

    params["key"] = my_api_key
    req = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json", params)
    return req.json()


def place(place_id, session_token=None, fields=None, language="English"):
    """
    Comprehensive details for an individual place.
    :param place_id: A textual identifier that uniquely identifies a place,
        returned from a Places search.
    :type place_id: string
    :param session_token: A random string which identifies an autocomplete
                          session for billing purposes.
    :type session_token: string
    :param fields: The fields specifying the types of place data to return,
                   separated by a comma. For full details see:
                   https://cloud.google.com/maps-platform/user-guide/product-changes/#places
    :type input: list
    :param language: The language in which to return results.
    :type language: string
    :rtype: result dict with the following keys:
        result: dict containing place details
        html_attributions: set of attributions which must be displayed
    """
    params = {"placeid": place_id}

    if fields:
        invalid_fields = set(fields) - PLACES_DETAIL_FIELDS
        if invalid_fields:
            raise ValueError("Valid values for the `fields` param for "
                             "`place` are '%s', these given field(s) "
                             "are invalid: '%s'" % (
                                 "', '".join(PLACES_DETAIL_FIELDS),
                                 "', '".join(invalid_fields)))
        params["fields"] = convert.join_list(",", fields)

    if language:
        params["language"] = language
    if session_token:
        params["sessiontoken"] = session_token
    params["key"] = my_api_key
    ret = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params)
    return ret.json()


def getReply(query):
    # query = "nearest eye doctor available"
    # output = find_place("hospital", "textquery", None, "point:23.420386, 85.434566")
    output = find_place(query, "textquery", None, "ipbias")
    # print(output)
    # print(output['candidates'])
    result = place(output['candidates'][0]['place_id'])

    return result, result['result']['name'], result['result']['formatted_address']#, result['result'][
        #'formatted_phone_number']

    # print(result)
    # print(result['result']['name'])
    # print(result['result']['formatted_address'])
    # print(result['result']['formatted_phone_number'])


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
    c = 0

    def __init__(self):
        # self.graph = tf.get_default_graph()
        # self.model = keras.models.load_model('../model/DiseasePredictor.h5')
        # print(model.summary())
        self.threshold = 0.65
        self.current_symptoms_yes = []
        self.current_symptoms_no = []

        self.symptom2vec = {}
        self.vec2symptom = {}
        self.all_possible_diseases = []
        self.all_possible_symptom = []
        self.number_of_top_diseases = 5
        self.current_disease_list = []
        self.query = ""
        self.last_asked = ""
        self.thres = 4
        self.new_map = {}
        self.c = 0

    for i in range(len(symptoms_list)):
        symptom2vec[symptoms_list[i]] = i
        vec2symptom[i] = symptoms_list[i]

    @staticmethod
    def getListOfSymptoms(one_hot):
        symptoms_return = []
        for iterate in range(len(one_hot)):
            if one_hot[iterate] == 1:
                symptoms_return.append([symptoms_list[iterate]])

        return symptoms_return

    @staticmethod
    def getOneHot(symptoms):
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
        print(self.current_symptoms_yes)
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
                        j = j.replace("_", " ")
                        ask = "Do you also have " + j + "?"
                        print(j, ask)
                        return j, ask

        else:
            current_disease_list_local = []
            self.c = 0
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
                if self.new_map[key] not in current_disease_list_local:
                    current_disease_list_local.append(self.new_map[key])
                print(key, self.new_map[key])
                # all_possible_symptoms.append(self.new_map[key])
                self.c += 1
                if self.c == 1:
                    break
            return "done", "You maybe suffering from " + current_disease_list_local[0] + "."

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
    print(data)

    if 'venue-medical-type' in data['queryResult']['parameters']:
        _, x, y = getReply(data['queryResult']['parameters']['venue-medical-type'])
        reply = x + " " + y # + " " + z


    # print(current_symptoms_yes)
    # print(current_symptoms_no)
    # print(query)
    # print(self.last_asked)
    else:
        obj_name = data['session']

        print(data)
        print(obj_name)

        if obj_name not in object_dict.keys():
            object_dict[obj_name] = iterator
            iterator += 1
            object_list.append(DiffSessions())

        exit_or_not, reply = object_list[object_dict[obj_name]].get_result(data)

        print(len(object_list))
        print(len(object_dict))

        if exit_or_not == "exit":
            object_dict[obj_name] = iterator
            iterator += 1

    reply = reply.replace("_", " ")
    dictionary = {'fulfillmentText': reply}
    # print(data['queryResult']['outputContexts']['lifespanCount'])
    # dictionary['outputContexts'] = data['queryResult']['outputContexts']

    return make_response(jsonify(dictionary))


if __name__ == "__main__":
    app.run()
