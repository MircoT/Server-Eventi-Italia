from __future__ import unicode_literals
import os, sys, signal, atexit, json
from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse
from citiesmanager import CitiesManager
import urllib

app = Flask(__name__)
api = restful.Api(app)
app.debug = True

CitiesManager(app)

class RestNewsR(restful.Resource):
    """Restful class with get, put and delete
    method for region input
    """
    def get(self, region):
        """Get method for news
        """
        app.logger.debug("region:" + str(region))
        if region == "list":
            return CitiesManager(app).regions_names()
        elif region == "init":
            return CitiesManager(app).init_db()
        elif region == "update":
            return CitiesManager(app).restart_update_news()
        elif region == "start":
            return CitiesManager(app).start_update_news()
        elif region == "stop":
            return CitiesManager(app).stop_update_news()
        return { 'error': "Unknown command"}
    
    def delete(self, region):
        """Delete method for region news
        """
        regions_names = CitiesManager(app).regions_names()['regions']
        if region == "all":
            return CitiesManager(app).delete_all()
        elif not any(region == name for name in regions_names):
            return { "error": "Unknown region"}
        else:
            return CitiesManager(app).delete_region_news(region)
    
    def put(self, region):
        """Insert a new region
        
        Data input must be in json
        """
        regions_names = CitiesManager(app).regions_names()['regions']
        if any(region == name for name in regions_names):
            return { "error": "Region already exist"}
        else:
            app.logger.debug(request.data)
            data = json.loads(request.data)
            new_region = {
                'name': region,
                'link': data['link']
            }
            return CitiesManager(app).insert("Regions", new_region)
    

class RestNewsC(restful.Resource):
    """Restful class with get, put and delete
    method for city and region input
    """
    def get(self, region, city):
        """Get method for news
        """
        city = urllib.unquote(city)
        
        regions_names = CitiesManager(app).regions_names()['regions']
        if not any(region == name for name in regions_names):
            return { "error": "Unknown region"}
        
        if city == "list":
            return CitiesManager(app).cities_names(region)
        else:
            cities_names = CitiesManager(app).cities_names(region)["cities"]
            if any(city == name for name in cities_names):
                #app.logger.debug("Selected %s" % city)
                return CitiesManager(app).city_events(city)
            else:
                return { "error": "Unknown city name"}

    def delete(self, region, city):
        """Delete method for cities news
        """
        city = urllib.unquote(city)
        
        regions_names = CitiesManager(app).regions_names()['regions']
        if not any(region == name for name in regions_names):
            return { "error": "Unknown region"}
        
        cities_names = CitiesManager(app).cities_names(region)["cities"]
        if any(city == name for name in cities_names):
            #app.logger.debug("Selected %s" % city)
            return CitiesManager(app).delete_city_news(city)
        else:
            return { "error": "Unknown city name"}
    
    def put(self, region, city):
        """Insert a new City
        
        Data input must be in json
        """
        regions_names = CitiesManager(app).regions_names()['regions']
        if not any(region == name for name in regions_names):
            return { "error": "Region not exist"}
        else:
            cities_names = CitiesManager(app).cities_names(region)["cities"]
            if any(city == name for name in cities_names):
                #app.logger.debug("Selected %s" % city)
                return { "error": "City already exist"}
            #app.logger.debug(request.data)
            data = json.loads(request.data)
            new_city = {
                'name': city,
                'link': data['link'],
                'region': region
            }
            return CitiesManager(app).insert("Cities", new_city)

class RestNewsN(restful.Resource):
    """Restful class with put method for news input
    """    
    def put(self, region, city, news):
        """Insert a new news
        
        Data input must be in json
        """
        regions_names = CitiesManager(app).regions_names()['regions']
        if not any(region == name for name in regions_names):
            return { "error": "Region not exist"}
        else:
            cities_names = CitiesManager(app).cities_names(region)["cities"]
            if not any(city == name for name in cities_names):
                #app.logger.debug("Selected %s" % city)
                return { "error": "City not exist"}
            #app.logger.debug(request.data)
            data = json.loads(request.data)
            new_news = {
                'city': city,
                'link': data['link'],
                'title': news,
                'img': data['img'],
                'text': data['text'],
                'period': data['period']
            }
            return CitiesManager(app).insert("News", new_news)
    

parser = reqparse.RequestParser()
parser.add_argument('command', type=str, required=False, help="A command for cities manager")

class RestNewsPost(restful.Resource):
    def post(self):
        app.logger.debug("POST REQUEST ON REST")
        args = parser.parse_args()
        app.logger.debug("ARGS: "+str(args))
        
        if args['command'] == "update":
            return CitiesManager(app).restart_update_news()
        elif args['command'] == "init":
            return CitiesManager(app).init_db()
        elif args['command'] == "start":
            return CitiesManager(app).start_update_news()
        elif args['command'] == "stop":
            return CitiesManager(app).stop_update_news()

api.add_resource(RestNewsPost, '/')
api.add_resource(RestNewsR, '/<string:region>')
api.add_resource(RestNewsC, '/<string:region>/<string:city>')
api.add_resource(RestNewsN, '/<string:region>/<string:city>/<string:news>')
    
def close_thread():
    """ Close thread function
    """
    CitiesManager(app).stop_update_news()

def ctrlC_handler(signal, frame):
    """ Handler for Ctrl+C event
    """
    CitiesManager(app).stop_update_news()

if __name__ == '__main__':
    #register signal
    signal.signal(signal.SIGINT, ctrlC_handler)
    #register closer method
    atexit.register(close_thread)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    cm = CitiesManager(app)
    app.run(host='0.0.0.0', port=port)