import json

import pandas as pd
from flask import Flask, jsonify
from flask_restplus import Resource, Api
from nltk.corpus import wordnet as wn
import nltk
nltk.download("wordnet")
nltk.download("wordnet_ic")

app = Flask(__name__)
api = Api(app)


def load_entities(entity_type):
    food = wn.synset('{}.n.01'.format(entity_type))
    return set([w.lower().replace("_", " ") for s in food.closure(lambda s: s.hyponyms()) for w in s.lemma_names()])


vegetables = load_entities("vegetable")
fruits = load_entities("fruit")


def load_data():
    companies = pd.read_json("resources/companies.json")
    people = pd.read_json("resources/people.json")
    df = people.merge(companies, left_on="company_id", right_on="index", how="left")
    # df.drop("index_y", axis=1, inplace=True)
    # df.drop("company_index", axis=1, inplace=True)
    df.rename(columns={'index_x': 'index', "index_y": "company_index"}, inplace=True)
    # df.set_index("index", inplace=True)
    companies = set(companies["index"].values)
    df["vegetables"] = df["favouriteFood"].apply(lambda f: [a for a in f if a in vegetables])
    df["fruits"] = df["favouriteFood"].apply(lambda f: [a for a in f if a in fruits])
    df.set_index("index", inplace=True)
    return companies, df


# Read and load data from the given sources
companies, dataset = load_data()


def error(code, message):
    error = jsonify({"message": message})
    error.status_code = code
    return error


@api.route('/companies/<int:company_index>/employees')
@api.param('company_index', 'company index')
class Company(Resource):
    @api.response(400, 'Company index is incorrect')
    @api.response(404, 'No employee found')
    @api.doc(
        description="Given a company, the API needs to return all their employees. Provide the appropriate solution if the company does not have any employees.")
    def get(self, company_index):
        if company_index not in companies:
            return error(400, "Company name is incorrect'")

        result = dataset.query("company_index=={}".format(company_index))
        if len(result) == 0:
            return error(404, "The company has no employees")

        return jsonify(json.loads(result.to_json(orient='records')))


@api.route('/people/<int:index>/favorite')
@api.param('index', 'person\'s index (0 to 999)')
class People(Resource):
    @api.response(404, 'Person not found')
    @api.doc(
        description='Given 1 people, provide a list of fruits and vegetables they like. This endpoint must respect this interface for the output: `{"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}`')
    def get(self, index):
        if index not in dataset.index:
            return error(404, "Person not found")

        result = json.loads(dataset.iloc[index].to_json())
        ret = dict()
        ret["username"] = result["name"]
        ret["age"] = str(result["age"])
        ret["fruits"] = result["fruits"]
        ret["vegetables"] = result["vegetables"]

        return jsonify(ret)


@api.route('/people/<int:index>/common-friends/<int:friend_index>')
@api.param('index', 'first person\'s index (0 to 999)')
@api.param('friend_index', 'second person\'s index (0 to 999)')
class Friends(Resource):
    @api.response(404, 'Person not found')
    @api.doc(
        description="Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common which have brown eyes and are still alive.")
    def get(self, index, friend_index):
        if index not in dataset.index or friend_index not in dataset.index:
            return error(404, "Person not found")

        p1_df = dataset.iloc[index]
        p1 = json.loads(p1_df[["name", "age", "address", "phone"]].to_json())
        p1_friends = [f["index"] for f in p1_df["friends"]]

        p2_df = dataset.iloc[friend_index]
        p2 = json.loads(p2_df[["name", "age", "address", "phone"]].to_json())
        p2_friends = [f["index"] for f in p2_df["friends"]]

        common_friends = list(set(p1_friends) & set(p2_friends))

        df = dataset
        df["index"] = dataset.index
        friends = list(df[df["index"].isin(common_friends)].query("has_died==False and eyeColor=='brown'").index.values)
        friends = [{"index": int(a)} for a in friends]
        response = {
            "people": [p1, p2],
            "common_friends": friends
        }

        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=False)
