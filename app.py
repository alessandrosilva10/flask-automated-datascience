import base64
import json
from functools import reduce

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource
import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True)


class MoviePredict(Resource):
    @cross_origin(supports_credentials=True)
    def post(self):
        try:
            data = request.get_json(silent=False)["csv"]
            data = list(reduce(lambda x, y: x + y, data.items()))
            data = pd.DataFrame(data[1])
        except ValueError as e:
            return e

        try:
            del data['rank'], data['movie_title'], data['release_date'], data['domestic_gross____']
        except ValueError as e:
            return e

        try:
            data["production_budget____"] = data["production_budget____"].str.replace("$", "").str.replace(",", "")
            data["worldwide_gross____"] = data["worldwide_gross____"].str.replace("$", "").str.replace(",", "")
            data["production_budget____"] = data["production_budget____"].apply(float)
            data["worldwide_gross____"] = data["worldwide_gross____"].apply(float)

        except ValueError as e:
            return e

        try:
            X = DataFrame(data, columns=['production_budget____'])
            y = DataFrame(data, columns=['worldwide_gross____'])
        except ValueError as e:
            print(e)
            return e

        try:
            regression = LinearRegression()
            regression.fit(X, y)
            print(type(X))
            print(type(y))
            #X = tuple(X.astype('U32'))
            #y = tuple(y)

            plt.figure(figsize=(10, 6))
            plt.scatter(X, y, alpha=0.3)
            #print(X)
            # print(y)

            #plt.plot(X, regression.predict("""np.array([X]).reshape(1, 1))""", X, color="red", linewidth=4)
            plt.plot(X, regression.predict(X), color="red", linewidth=4)

            #print(regression.predict(X))
            plt.title('Filme Cost vs Global Revenue')
            plt.xlabel('Production Budget $')
            plt.ylabel('Worldwide Gross $')
            plt.ylim(0, 3000000000)
            plt.xlim(0, 450000000)
            plt.savefig('foo.pdf')
            plt.savefig('foo.png', bbox_inches='tight')

            import base64
            import io
            pic_IObytes = io.BytesIO()
            plt.savefig(pic_IObytes, format='png')
            pic_IObytes.seek(0)
            pic_hash = base64.b64encode(pic_IObytes.read())

            #plt.show()
            return pic_hash
        except ValueError as e:
            print(e)

        
        return jsonify("my_base64_jpgData")


api.add_resource(MoviePredict, "/predict")


@app.route('/')
def index():
    return "Index"


if __name__ == "__main__":
    app.run(debug=True)
