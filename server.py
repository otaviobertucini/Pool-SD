import Pyro4
import threading
import re
from datetime import datetime, timedelta

from Pyro4.core import expose
# configura uma instância única do servidor para ser consumida por diversos
# clientes


def str2Date(date):

    return datetime.strptime(date, '%d/%m/%y %H:%M:%S')

def parseSuggestions(suggestions):

    exp = re.compile(' {0,}, {0,}')

    return re.sub(exp, ',', suggestions)

@Pyro4.expose
class Poll:

    title = ''
    owner = None
    dueDate = None
    place = ''
    suggestions = []
    voteCount = []
    opened = True
    subscribers = []

    def __init__(self, title, owner, dueDate, place, suggestions):

        self.title = title
        self.owner = owner
        self.dueDate = datetime.now() + timedelta(seconds=10)
        self.place = place
        self.suggestions = suggestions
        self.voteCount = [0] * len(suggestions)

    def getTitle(self):
        return self.title
        
    def getSuggestions(self):
        return self.suggestions

    def receiveVote(self, index, subscriber):
        self.subscribers.append(subscriber)
        self.voteCount[index] = self.voteCount[index] + 1

    def closePoll(self):

        print('ENTREEEEEEE')

        if(not self.opened):
            return

        self.opened = False

        winner = self.suggestions[self.suggestions.index(max(self.suggestions))]

        for subscriber in self.subscribers:
            print('ENTREEEEEEE2')
            subscriber.getReference().closedPoll(self.title, winner)
        if self.owner not in self.subscribers:
            self.owner.getReference().closedPoll(self.title, winner)

class ClientInstance:

    name = ''
    referece = ''
    publicKey = ''
    uri = ''

    def __init__(self, name, reference, key, uri):

        self.name = name
        self.referece = reference
        self.publicKey = key
        self.uri = uri

    def getUri(self):
        return self.uri

    def getName(self):
        return self.name

    def getReference(self):
        return self.referece
        
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):

    clients = []
    polls = []

    startDate = None

    def __init__(self):
        self.startDate = datetime.now() + timedelta(seconds=15)

    def getUser(self, uri):
        for client in self.clients:
            if client.getUri() == uri:
                return client

        raise Exception('Usuário não encontrado!')

    def getPoll(self, title):
        for poll in self.polls:
            if poll.getTitle() == title:
                return poll
        
        raise Exception('Enquete não encontrado!')
        

    #coesão e desacoplamento------------------------       MÃO DO SIMÃO
    def runServer(self):                              #$$$$$$$$$$$$$$$$$$$$$$$$$
        with Pyro4.Daemon() as daemon:                #$$$$$$$$$$$$$$$$$$$' '$$$
#registra a aplicação do servidor no serviço de nomes #$$$$$$$$$$$$$$$$$$$  $$$$
            uri = daemon.register(self)               #$$$$$$$'/ $/ `/ `$' .$$$$
            ns = Pyro4.locateNS()                     #$$$$$$'|. i  i  /! .$$$$$
            ns.register("SearchNameServer", uri)      #$$$$$$$'_'.--'--'  $$$$$$        
            print("Server is ready")                  #$$^^$$$$$'        J$$$$$$
            daemon.requestLoop()                      #$$$   ~""   `.   .$$$$$$$
                                                      #$$$$$',      ;  '$$$$$$$$                                                
                                                      #$$$$$$$$$$$.'   $$$$$$$$$

    @Pyro4.expose    
    def newPoll(self, uri, title, place, suggestions, dueDate):
        
        owner = self.getUser(uri)

        suggestions = parseSuggestions(suggestions).split(',')

        poll = Poll(title, owner, dueDate, place, suggestions)
        self.polls.append(poll)

        for client in self.clients:
            client.getReference().notification(title, suggestions)            

    def getPollSuggestions(self, title):

        poll = self.getPoll(title)
        if(poll.opened):
            return poll.getSuggestions()
        return False

    @Pyro4.expose
    def register(self, uri, name, key):

        client = Pyro4.Proxy(uri)

        instance = ClientInstance(name, client, key, uri)
        self.clients.append(instance)    

        print('Usuário ' + name + ' criado com sucesso!') 

    @Pyro4.expose
    def getClients(self):

        for client in self.clients:

            print('oie: ' + client.name)

    def pollVote(self, uri, title, chosenDate):
        user = self.getUser(uri)

        poll = self.getPoll(title)

        if(not poll.opened):
            print('Enquete encerrada!')
            return
        
        index = int(chosenDate) - 1

        poll.receiveVote(index, user)

        print('O usuário ' + user.getName() + ' votou na enquete ' + title + ' escolhendo: ' + poll.suggestions[index])

        if(sum(poll.voteCount) == len(self.clients)):
            poll.closePoll()

    def checkDueDate(self):

        while True:
            for poll in self.polls:
                if(datetime.now() >= poll.dueDate):
                    if(poll.opened):
                        poll.closePoll()


def main():
    server = Server()

    # thread = threading.Thread(target=server.checkDueDate)
    # thread.daemon = True
    # thread.start()
    
    server.runServer()

main()