'''
GLOBAL TODO:

- clean up html before running it through beautiful soup using html5lib (http://stackoverflow.com/questions/3198874/malformed-start-tag-error-python-beautifulsoup-and-sipie-ubuntu-10-04)
- possible crawler error: 'popular' is being found in http://www.buzzfeed.com/justinesharrock/google-mystery-barge-is-actually-a-sailboat (location is 4903 in database, but not when printing words list... it's types)
'''

import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import pymongo
import re

ignorewords = set(['the','of', 'a', 'to', 'and','in','is','it']) 

class crawler:
    # Initialize the crawler with the catbase database
    def __init__(self):
        # (TODO) connect to non-local mongod instance: http://docs.mongodb.org/manual/reference/connection-string/
        connection_string = "mongodb://localhost"
        self.conn = pymongo.MongoClient(connection_string)
        self.db = self.conn.catbasetest # FOR TESTING

    # Close the database
    def __del__(self):
        self.conn.close()

    # Index an individual page (TODO)
    def addtoindex(self, url, soup):
        if self.isindexed(url): return
        print 'Indexing ' + url

        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)
        #print "words: " + str(words) + '\n'

        # Link each word to this url
        for i in range(len(words)):
            #print "<-- i: " + str(i) + '\n'
            #print "<- url: " + str(url) + '\n'
            word = words[i]
            #print "word: " + str(word) + '\n'
            if word in ignorewords: continue
            db_word = self.db.words.find_one({'word': word}) # assumes there's never a duplicate for a given word
            #print "db_word: " + str(db_word) + '\n'
            if db_word is not None:
                j = 0
                isFound = False
                for db_url in db_word['urls']:
                    if db_url['url'] == url:
                        #print "db_word['urls'][j]: " + str(db_word['urls'][j]) + '\n'
                        #print "db_word['urls'][j]['locations']: " + str(db_word['urls'][j]['locations']) + '\n'
                        templist = db_word['urls'][j]['locations']
                        #print "templist: " + str(templist) + '\n'
                        if templist is not None:
                            templist.append(i)
                        else:
                            templist = [i]
                        db_word['urls'][j]['locations'] = templist
                        self.db.words.save(db_word)
                        isFound = True
                    j += 1
                if isFound == False:
                    db_word['urls'] = db_word['urls'] + [{'url': url,'locations': [i]}]
                    self.db.words.save(db_word)
                #print "updated db_word: " + str(db_word) + '\n'
            else:
                wordJSON = {'word': word, 'urls': [{'url': url, 'locations': [i]}]}
                #print "created db_word: " + str(wordJSON) + '\n'
                self.db.words.insert(wordJSON)

    # Extract the text from an HTML page (no tags)
    def gettextonly(self, soup):
        v = soup.string 
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # Separate the words by any non-whitespace character
    def separatewords(self, text):
        splitter = re.compile('\\W*') # (TODO) improve this (possibly use a stemming algorithm to remove suffixes from words)
        return [s.lower() for s in splitter.split(text) if s != '']

    # Return True if this url is already indexed
    def isindexed(self, url):
        for db_word in self.db.words.find():
            #print "each_word: " + str(db_word) + '\n'
            #print "each_word['urls']: " + str(db_word['urls']) + '\n'
            for db_url in db_word['urls']:
                #print "db_url: " + str(db_url) + '\n'
                if db_url['url'] == url:
                    return True
        return False

    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    # Starting with a list of pages, do a breadth-first
    # search to the given depth, indexing pages
    # as we go 
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                soup = BeautifulSoup(c.read())
                self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0] # remove location portion
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)

            pages = newpages







