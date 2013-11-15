'''
GLOBAL TODO:

- clean up html before running it through beautiful soup using html5lib (http://stackoverflow.com/questions/3198874/malformed-start-tag-error-python-beautifulsoup-and-sipie-ubuntu-10-04)
'''

import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import pymongo
import re
import nn
import os
#import bottle
#import pdb # FOR TESTING

ignorewords = set(['the','of', 'a', 'to', 'and','in','is','it']) 
mynet = nn.searchnet()


class crawler:
    # Initialize the crawler with the catbase database
    def __init__(self):
        # (TODO) connect to non-local mongod instance: http://docs.mongodb.org/manual/reference/connection-string/
        # connection_string = "mongodb://localhost"
        connection_string = os.environ.get("MONGOLAB_URI", 'mongodb://localhost/catbase')
        self.conn = pymongo.MongoClient(connection_string)
        self.db = self.conn.get_default_database()

    # Close the database
    def __del__(self):
        self.conn.close()

    # Index an individual page
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

class searcher:
    def __init__(self):
        # (TODO) connect to non-local mongod instance: http://docs.mongodb.org/manual/reference/connection-string/
        # connection_string = "mongodb://localhost"
        connection_string = os.environ.get("MONGOLAB_URI", 'mongodb://localhost/catbase')
        self.conn = pymongo.MongoClient(connection_string)
        self.db = self.conn.get_default_database()

    def __del__(self):
        self.conn.close()

    def getunrankedmatches(self, q):

        results = []
        finalresults = set()
        urls = set()

        # Split the words by spaces
        words = q.split(' ')
        #words.append('cat') #(TODO) when crawling enough add this back in

        print "[getunrankedmatches] words: " + str(words) + '\n'
        for word in words:
            db_word = self.db.words.find_one({'word': word}) # assumes there's never a duplicate for a given word
            if db_word is not None:
                for db_url in db_word['urls']:
                    results.append(db_url)
                    urls.add(db_url['url'])

        print "[getunrankedmatches] results: " + str(results) + '\n'
        for result in results:
            for url in urls:
                counter = 0
                for i in range(len(results)):
                    if results[i]['url'] == url:
                        counter += 1
                if counter == len(words):
                    finalresults.add(url)

        print "[getunrankedmatches] list(finalresults): " + str(list(finalresults)) + '\n'
        return list(finalresults)

    # take a dictionary of urls and scores and return a new dictionary with the same urls, but with scores between 0 and 1
    def normalizescores(self, scores, smallIsBetter = 0):

        vsmall = 0.00001 # Avoid division by zero errors
        if smallIsBetter:
            minscore = min(scores.values())
            return dict([(u, float(minscore)/max(vsmall,1)) for (u,l) in scores.items()])
        else:

            if scores is not None and len(scores.values()) > 0:
                maxscore = max(scores.values())
            else:
                maxscore = 0
            if maxscore == 0: maxscore = vsmall
            print "[normalizescores] normalizescores(scores): " + str(dict([(u, float(c)/maxscore) for (u,c) in scores.items()])) + '\n'
            return dict([(u, float(c)/maxscore) for (u,c) in scores.items()])

    def getscoredlist(self, words, results):
        totalscores = dict([(result, 0.0) for result in results])

        # (TODO) add more scores weighted with the neural network score
        weights = [(1.0, self.frequencyscore(words, results))] #(1.0, self.nnscore(words, results)) 

        print "[getscoredlist] weights: " + str(weights) + '\n'
        for (weight, scores) in weights:
            for url in totalscores:
                totalscores[url] += weight*scores[url]

        print "[getscoredlist] totalscores: " + str(totalscores) + '\n'
        return totalscores

    def query(self, q):
        results = self.getunrankedmatches(q)
        print "[query] results" + str(results) + '\n'
        words = q.split(' ')
        scores = self.getscoredlist(words, results)
        rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
        for (score, url) in rankedscores[0:10]:
            print '%f\t%s' % (score, url)

        print "[query] [r[1] for r in rankedscores[0:10]]: " + str([r[1] for r in rankedscores[0:10]]) + '\n'
        return words, [url[1] for url in rankedscores[0:10]]

    def frequencyscore(self, words, urls):
        counts = dict([(url,0) for url in urls])

        for word in words:
            db_word = self.db.words.find_one({'word': word}) # assumes there's never a duplicate for a given word
            if db_word is not None:
                for db_url in db_word['urls']:
                    for url in urls:
                        if db_url['url'] == url:
                            counts[db_url['url']] += len(db_url['locations'])

        print "[frequencyscore] counts: " + str(counts) + '\n'
        return self.normalizescores(counts)

    def nnscore(self, words, urls):
        nnres = mynet.getresult(words, urls)
        print "[nnscore] urls: " + str(urls) + '\n'
        scores = dict([(urls[i], nnres[i]) for i in range(len(urls))])
        
        print "[nnscore] scores: " + str(scores) + '\n'
        return self.normalizescores(scores)








