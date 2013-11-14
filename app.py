import bottle
import searchengine
import nn
import beaker.middleware

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

@bottle.route('/query', method='POST')
def queryhandler():
    e = searchengine.searcher()
    q = bottle.request.forms.get("query")
    mywords, myurls = e.query(q)
    s = bottle.request.environ.get('beaker.session')
    s['mywords'] = mywords
    s['myurls'] = myurls
    s.save()
    bottle.redirect('/results')

@bottle.route('/results')
def resultspage():
    s = bottle.request.environ.get('beaker.session')
    myurls = s['myurls']
    mywords = s['mywords']
    print "myurls: " + str(myurls) + '\n'
    print "mywords: " + str(mywords) + '\n'
    return bottle.template('results', words = mywords, urls = myurls)

bottle.debug(True)
bottle.run(app=app, host='localhost', port=8082) # (TODO) change this away from localhost to allcatseverything.net



