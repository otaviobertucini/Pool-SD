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
    dueDate = ''
    place = ''
    suggestions = []
    opened = True
    voteCounter = 0
    subscribers = []

    def __init__(self, title, owner, dueDate, place, suggestions):

        self.title = title
        self.owner = owner
        self.dueDate = dueDate
        self.place = place
        self.suggestions = suggestions

    def getTitle(self):
        return self.title

    #método para mostrar as opções de datas/horários para votação
        
    def getSuggestions(self):
        # i = 1
        for suggestion in self.suggestions:
            print(suggestion)
            # i += 1
        # print('ENTROU NO GETsUGGESTIONS')    
        # for index in range(len(self.suggestions)):
        #     print(index + 1, self.suggestions[index], end = '\n')    
        # print('SAIU NO GETsUGGESTIONS')

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
        self.startDate = datetime.now() + timedelta(seconds=5)

    def getUser(self, userName):
        for client in self.clients:
            if client.getName() == userName:
                return client.getName()

        raise Exception('Usuário não encontrado!')
        

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
    def newPoll(self, clientName, title, place, suggestions, dueDate):
        
        owner = self.getUser(clientName)

        poll = Poll(title, owner, dueDate, place, parseSuggestions(suggestions))
        self.polls.append(poll)

        for client in self.clients:
            client.getReference().notification(title, parseSuggestions(suggestions))            

    def getPollSuggestions(self, title):
        print('ENTROU NO GETpOLLsUGGESTIONS')
        print(title)
        for poll in self.polls:
            print(poll.getTitle)
            if poll.getTitle() == title:
                poll.getSuggestions()
        print('SAIU NO GETpOLLsUGGESTIONS')
        return poll.getSuggestions()
    # @Pyro4.expose
    # def test(self):                                 
    #     print("Não sei de nada")

    @Pyro4.expose
    def register(self, uri, name, key):

        # user = 

        # registra usuário, passa chave e referência do cliente
        client = Pyro4.Proxy(uri)

        instance = ClientInstance(name, client, key, uri)
        self.clients.append(instance)    

        print('Usuário ' + name + ' criado com sucesso!') 
        print(client)
        print(key)

    # def pollResquest(self):
    #     # chamar método do cliente para avisar nova enquete
    #     print('nada')

    @Pyro4.expose
    def getClients(self):

        for client in self.clients:

            print('oie: ' + client.name)

    def pollVote(self, userName, title, chosenDate):
        print('O usuário ' + userName + ' votou na enquete ' + title + ' escolhendo: ' + str(chosenDate))
        # user = self.getUser(userName)
        # print(user)
        # print('ACHEI: ')


    def closePoll(self, poll):
        pass

    def checkDueDate(self):

        while True:
            if(self.startDate < datetime.now()):
                print('passei!')

def main():
    server = Server()

    # thread = threading.Thread(target=server.checkDueDate)
    # thread.daemon = True
    # thread.start()
    
    server.runServer()

main()