'''
GLOBAL TODO:

- add in dtanh function (with self as first argument)
'''

from math import tanh
import pymongo
import os

class searchnet:
    def __init__(self):

        connection_string = os.environ.get("MONGOLAB_URI", 'mongodb://localhost/catbase')
        # connection_string = "mongodb://localhost"
        self.conn = pymongo.MongoClient(connection_string)
        self.db = self.conn.get_default_database()
        print self.db

    def __del__(self):
        self.conn.close()

    def dtanh(self, y):
        return 1.0-y*y

    def getstrength(self, from_node, to_node, layer):
        if layer == 0: #word->hidden
            db_edge = self.db.nn.find_one({'word': from_node, 'hiddenid': to_node})
            if db_edge is None:
                if layer == 0: return -0.2
                if layer == 1: return 0
            return db_edge['strength']
        else: #hidden->url
            db_edge = self.db.nn.find_one({'hiddenid': from_node, 'url': to_node})
            if db_edge is None:
                if layer == 0: return -0.2
                if layer == 1: return 0
            return db_edge['strength']

    def setstrength(self, from_node, to_node, layer, strength):
        if layer == 0: #word->hidden
            db_edge = self.db.nn.find_one({'word': from_node, 'hiddenid': to_node})
            if db_edge is None:
                edgeJSON = {'word': from_node, 'hiddenid': to_node, 'strength': strength}
                self.db.nn.insert(edgeJSON)
            else:
                db_edge['strength'] = strength
                self.db.nn.save(db_edge)
        else: #hidden->url
            db_edge = self.db.nn.find_one({'hiddenid': from_node, 'url': to_node})
            if db_edge is None:
                edgeJSON = {'hiddenid': from_node, 'url': to_node, 'strength': strength}
                self.db.nn.insert(edgeJSON)
            else:
                db_edge['strength'] = strength
                self.db.nn.save(db_edge)

    def generatehiddennode(self, words, urls):
        if len(words) > 3: return None

        # Check if we already created a hidden node for this set of words
        hiddenid = '_'.join(sorted([str(word) for word in words]))
        db_edge = self.db.nn.find_one({'hiddenid': hiddenid})

        # If not, create it
        if db_edge is None:
            for word in words:
                self.setstrength(word, hiddenid, 0, 1.0/len(words))
            for url in urls:
                self.setstrength(hiddenid, url, 1, 0.1)

    def getallhiddenids(self, words, urls):
        hiddenids = set()
        for word in words:
            db_edges = self.db.nn.find({'word': word})
            for db_edge in db_edges:
                hiddenids.add(db_edge['hiddenid'])
        for url in urls:
            db_edges = self.db.nn.find({'url': url})
            for db_edge in db_edges:
                hiddenids.add(db_edge['hiddenid'])
        return list(hiddenids)

    def setupnetwork(self, words, urls):
        # value lists
        self.words = words
        self.hiddenids = self.getallhiddenids(words, urls)
        self.urls = urls

        # node outputs
        self.ai = [1.0]*len(self.words)
        self.ah = [1.0]*len(self.hiddenids)
        self.ao = [1.0]*len(self.urls)

        # create weights matrix
        self.wi = [[self.getstrength(word, hiddenid, 0) for hiddenid in self.hiddenids] for word in self.words]
        self.wo = [[self.getstrength(hiddenid, url, 1) for url in self.urls] for hiddenid in self.hiddenids]

    # Takes a list of inputs, pushes them through the network, and returns the output of all the nodes in the output layer
    def feedforward(self):
        # the only inputs are the query words
        for i in range(len(self.words)):
            self.ai[i] = 1.0

        # hidden activations
        for j in range(len(self.hiddenids)):
            temp_sum = 0.0
            for i in range(len(self.words)):
                temp_sum = temp_sum + self.ai[i]*self.wi[i][j]
            self.ah[j] = tanh(temp_sum)

        # output activations
        for k in range(len(self.urls)):
            temp_sum = 0.0
            for j in range(len(self.hiddenids)):
                temp_sum = temp_sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(temp_sum)

        return self.ao[:]

    # Set up the network and use feedforward to get the outputs for a set of words and urls
    def getresult(self, words, urls):
        self.setupnetwork(words, urls)
        return self.feedforward()

    def backPropagate(self, targets, N=0.5):
        # calculate errors for output
        output_deltas = [0.0]*len(self.urls)
        for k in range(len(self.urls)):
            error = targets[k] - self.ao[k]
            #print "self.ao[k]: " + str(self.ao[k]) + '\n'
            output_deltas[k] = (1.0-self.ao[k]*self.ao[k])*error

        # calculate errors for hidden layer
        hidden_deltas = [0.0]*len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0.0
            for k in range(len(self.urls)):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = (1.0-self.ah[j]*self.ah[j])*error

        # update output weights
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urls)):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change

        # update input weights
        for i in range(len(self.words)):
            for j in range(len(self.hiddenids)):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change

    # Set up the network, run feedforward (so that the current output of every node will be stored in the instance variables), and run the backpropagation
    def trainquery(self, words, urls, selectedurl):
        # generate a hidden node if necessary
        self.generatehiddennode(words, urls)

        self.setupnetwork(words, urls)
        self.feedforward()
        targets = [0.0]*len(urls)
        targets[urls.index(selectedurl)] = 1.0
        self.backPropagate(targets)
        self.updatedatabase()

    def updatedatabase(self):
        # set them to database values
        for i in range(len(self.words)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.words[i], self.hiddenids[j], 0, self.wi[i][j])
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urls)):
                self.setstrength(self.hiddenids[j], self.urls[k], 1, self.wo[j][k])






