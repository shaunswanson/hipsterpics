'''
GLOBAL TODO:

'''

import urllib2
from urlparse import urljoin
import pymongo
import re
import nn
import os

ignorewords = set(['the','of', 'a', 'to', 'and','in','is', 'you', 'comments','it','points',':','hours','ago','days','months','years', 'point', 'reply','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','deleted','comment','OP','op','repost','imgur']) 
mynet = nn.searchnet()

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import InvalidElementStateException, TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import InvalidElementStateException, TimeoutException, NoSuchElementException

def initialize_driver():
    display=None
    #display = Display(visible=0, size=(800, 600))
    #display.start()

    profile = FirefoxProfile()
    profile.set_preference("dom.max_script_run_time", 600) # too short ???
    profile.set_preference("dom.max_chrome_script_run_time", 600) # too short ???
    profile.set_preference('permissions.default.image', 2) # disable images
    profile.set_preference('plugin.scan.plid.all', False) # disable plugin loading crap
    profile.set_preference('dom.disable_open_during_load', True) # disable popups
    profile.set_preference('browser.popups.showPopupBlocker', False)
    driver = webdriver.Firefox(profile) 
    driver.set_page_load_timeout(30)

    return (driver, display)



class crawler:
    # Initialize the crawler with the catbase database
    def __init__(self):
        connection_string = os.environ.get("MONGOLAB_URI", 'mongodb://localhost/catbase')
        self.conn = pymongo.MongoClient(connection_string)
        self.db = self.conn.get_default_database()
        print "NUMBER OF EDGES IN NEURAL NETWORK: " + str(self.db.nn.count()) + '\n'

    # Close the database
    def __del__(self):
        self.conn.close()

    # Index an individual page
    def addtoindex(self, content, picurl):
        if self.isindexed(picurl): 
            print "already indexed!" + '\n'
            return 

        # Get the individual words
        text = content
        print "text: " + str(text) + '\n'
        words = self.separatewords(text)
        print "words: " + str(words) + '\n'

        # Link each word to the picurl on the page
        for i in range(len(words)):
            #print "<-- i: " + str(i) + '\n'
            #print "<- url: " + str(url) + '\n'
            word = words[i]
            word = word.lower()
            #print "word: " + str(word) + '\n'
            if word in ignorewords: continue
            db_word = self.db.words.find_one({'word': word}) # assumes there's never a duplicate for a given word
            #print "db_word: " + str(db_word) + '\n'
            if db_word is not None:
                j = 0
                isFound = False
                for db_url in db_word['picurls']:
                    if db_url['picurl'] == picurl:
                        #print "db_word['urls'][j]: " + str(db_word['urls'][j]) + '\n'
                        #print "db_word['urls'][j]['locations']: " + str(db_word['urls'][j]['locations']) + '\n'
                        templist = db_word['picurls'][j]['locations']
                        #print "templist: " + str(templist) + '\n'
                        if templist is not None:
                            templist.append(i)
                        else:
                            templist = [i]
                        db_word['picurls'][j]['locations'] = templist
                        self.db.words.save(db_word)
                        isFound = True
                    j += 1
                if isFound == False:
                    db_word['picurls'] = db_word['picurls'] + [{'picurl': picurl,'locations': [i]}]
                    self.db.words.save(db_word)
                print "updated db_word: " + str(db_word) + '\n'
            else:
                wordJSON = {'word': word, 'picurls': [{'picurl': picurl, 'locations': [i]}]}
                print "created db_word: " + str(wordJSON) + '\n'
                self.db.words.insert(wordJSON)

    # Separate the words by any non-whitespace character
    def separatewords(self, text):
        splitter = re.compile('\\W*') # (TODO) improve this (possibly use a stemming algorithm to remove suffixes from words)
        return [s.lower() for s in splitter.split(text) if s != '']

    # Return True if this url is already indexed
    def isindexed(self, url):
        for db_word in self.db.words.find():
            #print "each_word: " + str(db_word) + '\n'
            #print "each_word['urls']: " + str(db_word['urls']) + '\n'
            for db_url in db_word['picurls']:
                #print "db_url: " + str(db_url) + '\n'
                if db_url['picurl'] == url:
                    return True
        return False

    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    # Starting with a list of pages, do a breadth-first
    # search to the given depth, indexing pages
    # as we go 
    def crawl(self, pages, depth=5):
        for i in range(depth):
            newpages = set()
            for page in pages:
                # (TODO) will freeze after this prints sometimes...
                print "<-- crawling " + str(page) + '\n' 
                driver, display = initialize_driver()
                try: 
                    driver.get(page)
                    comment_content_elements = driver.find_elements_by_xpath('//div[contains(@id,"captions")]')
                    comment_content = None
                    
                    # (TODO) may be missing this quite often
                    if len(comment_content_elements) > 0:
                        comment_content = comment_content_elements[0].text.encode("utf-8", "ignore")
                    picurls = driver.find_elements_by_xpath('//div[contains(@class,"stipple-dottable-wrapper")]/img')
                    if len(picurls) < 1:
                        picurls = driver.find_elements_by_xpath('//div[contains(@id,"image")]/div/img')
                    if len(picurls) < 1:
                        picurls = driver.find_elements_by_xpath('//div[contains(@class,"image")]/div/div/a/img')
                    if len(picurls) < 1:
                        picurls = driver.find_elements_by_xpath('//div[contains(@class,"stipple-dottable-wrapper")]/a/img')
                    if len(picurls) > 0:
                        realpicurl = picurls[0].get_attribute('src')
                        if realpicurl.find("gif") != -1:
                            realpicurl = None
                    else:
                        realpicurl = None 

                    print "realpicurl: " + str(realpicurl) + '\n'
                    links = driver.find_elements_by_xpath('//a[contains(@href,"gallery")]')
                    print "len(links): " + str(len(links)) + '\n'
                    for link in links:
                        reallink = link.get_attribute('href')
                        #print "reallink: " + str(reallink) + '\n'
                        newpages.add(reallink)
                except:
                    print "Could not open %s" % page
                    #continue
                    raise # FOR TESTING

                if realpicurl is not None:
                    if comment_content is not None:
                        self.addtoindex(comment_content, realpicurl)
                driver.close()

            pages = newpages
            print "pages: " + str(pages) + '\n'

class searcher:
    def __init__(self):
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
                for db_url in db_word['picurls']:
                    results.append(db_url)
                    urls.add(db_url['picurl'])

        print "[getunrankedmatches] results: " + str(results) + '\n'
        for result in results:
            for url in urls:
                counter = 0
                for i in range(len(results)):
                    if results[i]['picurl'] == url:
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
        weights = [(0.35, self.frequencyscore(words, results)), (0.65, self.nnscore(words, results))]

        print "[getscoredlist] weights: " + str(weights) + '\n'
        for (weight, scores) in weights:
            for url in totalscores:
                totalscores[url] += weight*scores[url]

        print "[getscoredlist] totalscores: " + str(totalscores) + '\n'
        return totalscores

    def query(self, q):
        results = self.getunrankedmatches(q)
        print "[query] results" + str(results) + '\n'
        words = q.lower().split(' ')
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
                for db_url in db_word['picurls']:
                    for url in urls:
                        if db_url['picurl'] == url:
                            counts[db_url['picurl']] += len(db_url['locations'])

        print "[frequencyscore] counts: " + str(counts) + '\n'
        return self.normalizescores(counts)

    def nnscore(self, words, urls):
        nnres = mynet.getresult(words, urls)
        print "[nnscore] urls: " + str(urls) + '\n'
        scores = dict([(urls[i], nnres[i]) for i in range(len(urls))])
        
        print "[nnscore] scores: " + str(scores) + '\n'
        return self.normalizescores(scores)








