import json

from flask import Flask, make_response, jsonify, abort
from flask_restplus import Resource, Api
import pandas as pd

app = Flask(__name__)
api = Api(app)


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


@api.route('/people')
class People(Resource):
    def get(self):
        return "Hello"


if __name__ == '__main__':
    app.run(debug=False)
