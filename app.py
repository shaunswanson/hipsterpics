#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
import searchengine
import nn
import beaker.middleware
import os

mynet = nn.searchnet()

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}
app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

@bottle.route('/') 
def querypage():
    return bottle.template('query')

@bottle.route('/resume')
def resumepage():
    return bottle.template('resume')

@bottle.route('/query', method='POST')
def queryhandler():
    try:
        e = searchengine.searcher()
        q = bottle.request.forms.get("query")
        mywords, myurls = e.query(q)
        s = bottle.request.environ.get('beaker.session')
        s['mywords'] = mywords
        s['myurls'] = myurls
        s.save()
        bottle.redirect('/results')
    except TimeoutException: 
        bottle.redirect('/TimeoutException')

@bottle.route('/TimeoutException')
def timeoutpage():
    return bottle.template('timeout')

@bottle.route('/results')
def resultspage():
    s = bottle.request.environ.get('beaker.session')
    myurls = s['myurls']
    mywords = s['mywords']
    print "myurls: " + str(myurls) + '\n'
    print "mywords: " + str(mywords) + '\n'
    return bottle.template('results', words = mywords, urls = myurls)

#API

@bottle.route('/trainquery')
def trainqueryhandler():
    s = bottle.request.environ.get('beaker.session')
    winnerurl = bottle.request.query['winnerurl']
    print s['mywords'], s['myurls'], winnerurl
    mynet.trainquery(s['mywords'], s['myurls'], winnerurl)
    # return "{'status':'success'}"
    bottle.redirect('/')

bottle.debug(True)
port = int(os.environ.get("PORT", 8082))
bottle.run(app=app, host='0.0.0.0', port=port) 



