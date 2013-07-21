# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from bs4 import BeautifulSoup
from thinbrowser import ThinBrowser


class UmbriaEvents(object):
    """Class to manage download events from Umbria's site
    """
    def __init__(self, app):
        self._browser = ThinBrowser()
        self.app = app
        self._url = "http://www.umbriaeventi.com/"
        self._page_gen = self._url + "eventi.php?menid=&comune=%s&page=%s"

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
        cities_l = soup.find("div", {'class': "links-comuni"}).\
            findNext("div", {'class': "links-body"}).\
            findAll("li")
        
        #self.app.logger.debug("Download Cities")
        for city in cities_l:
            city_name = city.text.replace("Eventi", "").strip()
            city_link = self._url + city.a['href']
            cities_urls[city_name] = city_link
        return cities_urls
    
    def get_events(self, url):
        """Return all event from a city
        """
        soup = self.get_soup(url)
        
        #####
        # To Do:
        #   to grab js page we must use a web driver like selenium
        # -------------------------
        #scripts = soup.findAll("script")
        #num_comune = ""
        #for script in scripts:
        #    if script.text.find("comune=") > 0:
        #        num_comune = script.text.split("comune=")[1].split("&")[0]
        #        break
        #print(num_comune)
        #
        #for num in range(0,5):
        #    url = self._page_gen % (num_comune, num)
        #    print(url)
        #    soup = self.get_soup(url)
        #    events = soup.find("div", {'class': "eventi-lista"}).\
        #        findAll("div", {'class': "eventi-lista-value"})
        #    evt = events[0].find("div", {'class': "eventi-lista-value-titolo"})
        #    print(evt)
        
        events = soup.find("div", {'class': "eventi-lista"}).\
            findAll("div", {'class': "eventi-lista-value"})
        
        events_list = list()
        for event in events:
            event_obj = dict()
            evt = event.find("div", {'class': "eventi-lista-value-titolo"})
            title = evt.a.text
            #print(title)
            event_obj['title'] = title
            link = self._url + evt.a['href']
            soup = self.get_soup(link)
            try:
                link = soup.find("div", {'class': "network-col1-text"}).\
                    a['href']
            except AttributeError:
                pass
            #print(link)
            event_obj['link'] = link
            evt_img = event.find("div", {'class': "eventi-lista-value-logo"})
            img = self._url + evt_img.img['src']
            #print(img)
            event_obj['img'] = img
            period = event.\
                find("div", {'class': "eventi-lista-value-info2"}).text
            #print(period)
            event_obj['period'] = period
            text = event.\
                find("div", {'class': "eventi-lista-value-descrizione"}).text
            #print(unidecode(text))
            event_obj['text'] = text
            events_list.append(event_obj)
        
        return events_list   