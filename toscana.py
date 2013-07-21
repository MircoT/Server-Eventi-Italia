# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from vars import convertName
from bs4 import BeautifulSoup
from thinbrowser import ThinBrowser


class ToscanaEvents(object):
    """Class to manage download events from Toscana's site
    """
    def __init__(self, app):
        self._browser = ThinBrowser()
        self.app = app
        self._url = "http://www.eventiintoscana.it/"

    def get_soup(self, url):
        """Return beautifulsoup obj from html url
        """
        response_page = self._browser.urlopen(url)
        html_page = self._browser.gzipPage(response_page)
        return BeautifulSoup(html_page)

    def download_cities(self):
        """Download all cities names and their links
        """
        cities_urls = dict()
        soup = self.get_soup(self._url)
        cities_l = soup.find(text = "Eventi in Provincia").\
            findNext("table").findAll("td")
        
        #self.app.logger.debug("Download Cities")
        for city in cities_l:
            city_name = city.img['alt'].replace("eventi", "").strip()
            city_link = city.a['href']
            cities_urls[convertName(city_name)] = city_link
        return cities_urls

    
    def get_events(self, url):
        """Return all event from a city
        """
        soup = self.get_soup(url)
        
        events = soup.findAll("div", {'class': "blog"})
        events_list = list()
        for event in events:
            event_obj = dict()
            period = event.\
                find("span", {'class': "titolino2"}).text.strip()
            event_obj['period'] = period
            
            last_period = period.split("al")[1].strip().split()[-1]
            
            title = event.\
                find("span", {'class': "titolino1"}).text.strip()
            
            #self.app.logger.debug("last_period : " + last_period)
            #self.app.logger.debug("title : " + title)
            
            try:
                title = title.split(last_period)[1].split("|")[0]
                event_obj['title'] = title
            except IndexError:
                last_period = period.split("al")[1].strip().split()[-2].capitalize()
                
            try:
                #self.app.logger.debug("last_period : " + last_period)
                title = title.split(last_period)[1].split("|")[0]
                event_obj['title'] = title
            except IndexError:
                event_obj['title'] = title
                
                
            #print(unidecode(title))
            
            img = event.\
                find("img", {'class': "lazy"})['data-href']
            #print(img)
            event_obj['img'] = img
            
            text = event.\
                find("div", {'class': "entry"}).findNext("p").text
            #print(unidecode(text))
            event_obj['text'] = text
            
            link = event.\
                find("span", {'class': "titolino1"}).a['href']
            #print(link)
            event_obj['link'] = link
            events_list.append(event_obj)
        
        return events_list    