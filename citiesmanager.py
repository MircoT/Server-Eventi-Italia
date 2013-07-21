from __future__ import unicode_literals
from vars import singleton
from thinbrowser import ThinBrowser
import threading
from alchemymanager import NewsDB, Regions, Cities, News
from umbria import UmbriaEvents
from toscana import ToscanaEvents
from unidecode import unidecode


class UpdateDB(threading.Thread):
    """Thread that update the DB
    """
    def __init__(self, app, news_db, umbria, toscana):
        self.browser = ThinBrowser()
        self.app = app
        self._news_db = news_db
        self._umbria = umbria
        self._toscana = toscana
        self.runnable = True
        self.waitEvent = threading.Event()
        super(UpdateDB, self).__init__()
    
    def stop(self):
        """Stop the thread
        """
        self.waitEvent.set()
    
    def start_(self):
        """Start the thread
        """
        self.runnable = True
        self.waitEvent.clear()
    
    def run(self):
        """Main function of the thread
        """
        while self.runnable:
            
            #DEBUG default update time
            #self.waitEvent.wait(43200)
            
            if not self.runnable:
                break
            if self.waitEvent.is_set():
                self.waitEvent.wait()
            
            session = self._news_db.session_m()
            regions = session.query(Regions).all()
            regions = dict([(reg.id_, reg.name) for reg in regions])
            cities = session.query(Cities).join(Regions).order_by(Cities.name).all()
            session.close()
            
            self.articles = dict()
            self.app.logger.debug("Star download news")
            for city in cities:
                if not self.runnable:
                    break
                else:
                    self.app.logger.debug("Download "+unidecode(city.name))
                    news_l = None
                    if regions[city.region] == "Umbria":
                        news_l = self._umbria.get_events(city.link)
                    elif regions[city.region] == "Toscana":
                        news_l = self._toscana.get_events(city.link)
                    else:
                        return
                    for news in news_l:
                        new_news = {
                            'title': news['title'],
                            'link': news['link'],
                            'period': news['period'],
                            'img': news['img'],
                            'text': news['text'],
                            'city': city.name
                        }
                        self._news_db.insert(News, new_news)
                    #Debug
                    #self._news_db.test_search()            
            return
            #CitiesManager(self.app).update()

@singleton
class CitiesManager(object):
    """Class to interact with the database alchemy
    """
    def __init__(self, app):
        self.app = app
        self._news_db = NewsDB(app)
        self._umbria = UmbriaEvents(app)
        self._toscana = ToscanaEvents(app)
        self._tre = UpdateDB(app, self._news_db, self._umbria, self._toscana)
        self.__insert_cities()
        self.start_update_news()
    
    def delete_all(self):
        """Clears completly the db
        """
        self._tre.runnable = False
        self._tre.join()
        self._news_db.delete_all()
        return {"message": "Db erased"}
    
    def init_db(self):
        """Recovers the initial state of the db
        and restart the update
        """
        self.stop_update_news()
        self._news_db.delete_all()
        self._news_db.base_population()
        self.__insert_cities()
        self.restart_update_news()
        return {"message": "app restarted"}
  
    def __insert_cities(self):
        """Insert cities in the database
        """
        session = self._news_db.session_m()
        regions = session.query(Regions).all()
        self.app.logger.debug("Start download cities")
        for region in regions:
            cities = None
            if region.name == "Umbria":
                cities = self._umbria.download_cities().items()
            elif region.name == "Toscana":
                cities = self._toscana.download_cities().items()
            
            for name, link in cities:
                self.app.logger.debug("Add city: "+unidecode(name))
                new_city = {
                    'name': name,
                    'link': link,
                    'region': region.name
                }
                self._news_db.insert(Cities, new_city)
        session.close()
        #Debug
        #self._news_db.test_search()
       
    def restart_update_news(self):
        """Start global update and if is already started
        he stops the update and restarts it
        """
        self._tre.runnable = False
        self._tre.join()
        del self._tre
        self._news_db.delete_all_news()
        self._tre = UpdateDB(self.app, self._news_db, self._umbria, self._toscana)
        self._tre.start()
        return { 'message': 'Update restarted'}
    
    def stop_update_news(self):
        """Stop the update"""
        self._tre.stop()
        return { 'message': 'Update stopped'}
    
    def start_update_news(self):
        """Start the update"""
        #Debug
        #self.app.logger.debug(self._tre.isAlive())
        if not self._tre.isAlive():
            try:
                self._tre.start()
            except RuntimeError: # if is already started
                pass
        if self._tre.runnable is False:
            self._tre.start_()
        return { 'message': 'Update started'}
        
    def city_events(self, city):
        """Return a list of events and a descriptio for a city
        """
        session = self._news_db.session_m()
        news_l = list()
        news_res = session.query(News).join(Cities).\
            filter(Cities.name == city).\
            order_by(News.id_).all()
        for news in news_res:
            news_l.append(news.web_return())
        session.close()
        return {"feeds": news_l}

    def cities_names(self, region):
        """Return a list of cities names in the regions selected
        """
        session = self._news_db.session_m()
        cities = session.query(Cities).join(Regions).\
            filter(Regions.name == region).\
            order_by(Cities.name).all()
        session.close()
        return {'cities': [city.name for city in cities]}
    
    def insert(self, type_, obj):
        if type_ == "Regions":
            return {"message": self._news_db.insert(Regions, obj)}
        elif type_ == "Cities":
            return {"message": self._news_db.insert(Cities, obj)}
        elif type_ == "News":
            return {"message": self._news_db.insert(News, obj)}
    
    
    def regions_names(self, ):
        """Return a list of all regions avaible
        """
        session = self._news_db.session_m()
        regions = session.query(Regions).all()
        session.close()
        return {'regions': [region.name for region in regions]}
    
    def delete_region_news(self, region):
        """Delete all news of a region
        """
        return self._news_db.delete_region_news(region)
    
    def delete_city_news(self, city):
        """Delete all news of a city
        """
        return self._news_db.delete_city_news(city)