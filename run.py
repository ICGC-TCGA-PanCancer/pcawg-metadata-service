from flask import Flask, Response, json, request
from flask.ext.cors import cross_origin
from elasticsearch import ElasticsearchException, Elasticsearch
from get_donor import get_donor
import pprint

VERSION = 'v0'

# create app
app = Flask(__name__)
app.config.from_object('dev_settings')
app.config.from_envvar('PROD_SETTINGS', silent=True)

#pprint.pprint( app.config )

def app_init(app):
	app.es = Elasticsearch([app.config["ES_HOST"]],
                           port=app.config["ES_PORT"])


# define routes
@app.route('/api/' + VERSION + '/donor/search', methods=['GET', 'OPTIONS'])
@cross_origin()
def donor_search():
    data = get_donor(request)

    return Response(json.dumps(data), mimetype='mimetype')


@app.route('/api/' + VERSION + '/donor/<donor_unique_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def donor(donor_unique_id):
	return donor_unique_id


# run app
if __name__ == "__main__":
    app_init(app)
    app.run(host=app.config["API_HOST"], port=app.config["API_PORT"], debug=app.config["DEBUG"])
