import json

from flask import Flask, make_response, jsonify, abort
from flask_restplus import Resource, Api
import pandas as pd
from nltk.corpus import wordnet as wn

app = Flask(__name__)
api = Api(app)


def load_entities(entity_type):
    from nltk.corpus import wordnet as wn
    food = wn.synset('{}.n.01'.format(entity_type))
    return set([w.lower().replace("_", " ") for s in food.closure(lambda s: s.hyponyms()) for w in s.lemma_names()])


def load_data():
    companies = pd.read_json("resources/companies.json")
    people = pd.read_json("resources/people.json")
    people.set_index("index", inplace=True)
    df = people.merge(companies, left_on="company_id", right_on="index")
    df = df.drop(["index"], axis=1)
    companies = set(companies["company"].values)
    return companies, df


# Read and load data from the given sources
companies, dataset = load_data()
vegetables = load_entities("vegetable")
fruits = load_entities("fruit")


def error(code, message):
    error = jsonify({"message": message})
    error.status_code = code
    return error


@api.route('/companies/<string:company_name>/employees')
@api.param('company_name', 'company name')
class Company(Resource):
    @api.response(400, 'Company name is incorrect')
    @api.response(404, 'Employee not found')
    def get(self, company_name):
        if company_name not in companies:
            return error(400, "Company name is incorrect'")

        result = dataset.query("company=='{}'".format(company_name))
        if len(result) == 0:
            return error(404, "The company has no employees")

        result = json.loads(result.to_json(orient='index'))
        return jsonify([result[i] for i in result])


@api.route('/people/<string:id>/favorite')
class People(Resource):
    @api.response(404, 'Person not found')
    def get(self, id):
        result = dataset.query("_id=='{}'".format(id))[["name", "age", "favouriteFood"]]

        if len(result) == 0:
            return error(404, "Person not found")

        result = json.loads(result.iloc[0].to_json())
        ret = dict()
        ret["username"] = result["name"]
        ret["age"] = str(result["age"])
        ret["fruits"] = [f for f in result["favouriteFood"] if f.lower() in fruits]
        ret["vegetables"] = [f for f in result["favouriteFood"] if f.lower() in vegetables]

        return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=False)
