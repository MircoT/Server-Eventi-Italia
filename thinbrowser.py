"""A simple class to download html page and unzip contents
"""
from __future__ import print_function, unicode_literals
import urllib2, gzip
from StringIO import StringIO

class ThinBrowser(object):
    """
    Basic Browser class
    """
    @staticmethod
    def urlopen(url):
        """
        Open an url with urllib2 with header
        """
        response = object()
        try :
            request = urllib2.Request(url.encode("ascii","ignore"))
            request.add_header('User-agent',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36')
            request.add_header("Accept-Language", "en-US")
            request.add_header('Accept-Encoding', 'gzip')
            response = urllib2.urlopen(request)
            #print("LEN =",response.info()["Content-length"])
            return(response)
        except urllib2.URLError as e:
            # TEST
            #print("EROOR ->", e)
            #print("EROOR ->", e.code)
            return ThinBrowser.urlopen(url)
        except RuntimeError as e:
            return False

    @staticmethod
    def getLastMod(page):
        """Return the date of the last modified in the response
        """
        return page.info().get("Last-Modified")
    
    
    @staticmethod
    def gzipPage(page):
        """
        Get data after GET request with gzip encoding
        """
        #if not hasattr(page,"info"):
        #    return("")
        data = object()
        # Check if content encoding is gzip
        if page.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(page.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else :
            data = page.read()
        return(data)
    