from __future__ import unicode_literals, print_function
import os
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from vars import singleton
from unidecode import unidecode


BASE = declarative_base()


class Regions(BASE):
    """Class for region objects
    """
    __tablename__ = "regions"

    id_ = Column(Integer, primary_key = True)
    name = Column(String)
    link = Column(String)

    def __init__(self, **kwargs):
        """"""
        self.name = kwargs['name']
        self.link = kwargs['link']
    
    def __repr__(self):
        """"""
        return "<Region('%d','%s','%s')>" % (
                self.id_, self.name, self.link)


class Cities(BASE):
    """Class for city objects
    """
    __tablename__ = "cities"

    id_ = Column(Integer, primary_key = True)
    name = Column(String)
    link = Column(String)
    region = Column(Integer, ForeignKey("regions.id_"))
    # Relations
    region_r = relationship(Regions, backref=backref("cities_l", cascade="all,delete-orphan"))

    def __init__(self, **kwargs):
        """"""
        self.name = kwargs['name']
        self.link = kwargs['link']
    
    def __repr__(self):
        """"""
        return "<City('%d','%s','%s','%s')>" % (
                self.id_, unidecode(self.name), # DEBUG with unidecode
                self.link, self.region)


class News(BASE):
    """Class for News objects
    """
    __tablename__ = "news"

    id_ = Column(Integer, primary_key = True)
    title = Column(String)
    link = Column(String)
    period = Column(String)
    text = Column(String)
    img = Column(String)
    #region = Column(Integer, ForeignKey("regions.id_"))
    city = Column(Integer, ForeignKey("cities.id_"))
    # Relations
    cities_r = relationship(Cities,
        backref=backref("news_l", cascade="all,delete-orphan")
    )
    
    
    def __init__(self, **kwargs):
        """"""
        self.title = kwargs['title']
        self.link = kwargs['link']
        self.period = kwargs['period']
        self.text = kwargs['text']
        self.img = kwargs['img']
    
    def __repr__(self):
        """"""
        return "<News ('%d','%s','%s','%s','%s','%s','%s')>" % (
                self.id_, self.title, self.link,
                self.period, self.text, self.img,
                self.city)
    
    def web_return(self):
        return {
            'title': self.title,
            'link': self.link,
            'period': self.period,
            'img': self.img,
            'text': self.text
        }
    

@singleton
class NewsDB(object):
    """Class to manage the database
    """
    def __init__(self, app):
        """"""
        self.app = app
        if os.path.exists("events.db"):
            os.remove("events.db")
        self.engine = create_engine("sqlite:///events.db", echo = False)
        self.base = BASE
        # create tables
        self.base.metadata.create_all(self.engine)
        self.session_m = sessionmaker(bind = self.engine)
        self.base_population()
    
    def base_population(self):
        """Insert the base regions
        """
        self.insert(Regions, {
            'name': "Umbria",
            'link': "http://www.umbriaeventi.com/"
            }
        )
        self.insert(Regions, {
            'name': "Toscana",
            'link': "http://www.eventiintoscana.it/"
            }
        )
    
    def insert(self, type_, obj):
        """Fits objects in database
        
        Args:
            type_: class, this is the type
               class of the object to
               insert
            obj: dict, this is the object
                to insert
        """
        session = self.session_m()
        if type_ is Regions:
            new_region = Regions(
                name = obj['name'],
                link = obj['link']
            )
            session.add(new_region)
            session.commit()
            return True
        elif type_ is Cities:
            new_city = Cities(
                name = obj['name'],
                link = obj['link'],
            )
            region = session.query(Regions).\
                filter(Regions.name == obj['region']).first()
            region.cities_l.append(new_city)
            session.add(new_city)
            session.commit()
            return True
        elif type_ is News:
            new_news = News(
                title = obj['title'],
                link = obj['link'],
                period = obj['period'],
                img = obj['img'],
                text = obj['text']  
            )
            city = session.query(Cities).\
                filter(Cities.name == obj['city']).first()
            city.news_l.append(new_news)
            session.add(new_news)
            session.commit()
            return True
        session.close()
        return False
    
    def delete_city_news(self, city):
        """Delete all news of the selected city
        """
        session = self.session_m()
        res = session.query(News).join(Cities).\
            filter(Cities.name==city).all()
        for news in res:
            #self.app.logger.debug("Delete news")
            session.delete(news)
        session.commit()
        session.close
        return {"city news": "deleted"}
    
    def delete_region_news(self, region):
        """Delete all news of the selected region
        """
        session = self.session_m()
        res = session.query(News).join(Cities).join(Regions).\
            filter(Regions.name == region).all()
        for news in res:
            #self.app.logger.debug("Delete news")
            session.delete(news)
        session.commit()
        session.close()
        return {"region news": "deleted"}

    def delete_all_news(self):
        """Delete all nes for a new update"""
        session = self.session_m()
        news_l = session.query(News).all()
        for news in news_l:
            session.delete(news)
        session.commit()
        session.close()
  
    def delete_all(self):
        """Delete all regions and the others object with relationships"""
        session = self.session_m()
        res = session.query(Regions).all()
        for region in res:
            session.delete(region)
        session.commit()
        session.close()

    def test_search(self):
        """Function to print database content
        """
        session = self.session_m()
        #res = session.query(News).filter(News.region=="Umbria").all()
        res = session.query(News).all()
        print("NEWS")
        for r in res:
            print(r)
            #print("\tid: " + str(r.id_))
            #print("\ttitle: " + r.title)
            #print("\tlink: " + r.link)
            #print("\tregion: " + str(r.region))
            #print("\tcity:" + str(r.city))
            print("+++++")
        #print("-----")
        #print("Toscana NEWS")
        #res = session.query(News).filter(News.region=="Toscana").all()
        #for r in res:
        #    print(r)
        #    #print("\tid: " + str(r.id_))
        #    #print("\ttitle: " + r.title)
        #    #print("\tlink: " + r.link)
        #    #print("\tregion: " + str(r.region))
        #    #print("\tcity:" + str(r.city))
        #    print("+++++")
        print("-----")
        print("CITIES")
        res = session.query(Cities).all()
        for r in res:
            print(r)
            #print("\tid: " + str(r.id_))
            #print("\tname: " + r.name)
            #print("\tlink: " + r.link)
            #print("\tregion: " + str(r.region))
            print("+++++")
        #print("NEWS IN PERUGIA")
        #res2 = session.query(News).select_from(join(Cities, News)).filter(Cities.name == "Perugia").all()
        #print("-----")
        #for r in res2:
        #    print(r)
        #    #print("\tid: " + str(r.id_))
        #    #print("\ttitle: " + r.title)
        #    #print("\tlink: " + r.link)
        #    #print("\tregion: " + str(r.region))
        #    #print("\tcity: " + str(r.city))
        #    print("+++++")
        #print("-----")
        res = session.query(Regions).all()
        print("REGIONS")
        for r in res:
            print(r)
            #print("\tid: " + str(r.id_))
            #print("\tname: " + r.name)
            #print("\tlink: " + r.link)
            print("+++++")