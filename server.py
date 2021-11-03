import Pyro4
import threading
import re
from datetime import datetime, timedelta
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Pyro4.core import expose
# configura uma instancia unica do servidor para ser consumida por diversos clientes
# -*- coding: utf-8 -*-

#formata o string para datetime no modelo descrito
def str2Date(date):
    return datetime.strptime(date, '%d/%m/%Y %H:%M:%S')

#garante que não haja espaços excedentes na string
def parseSuggestions(suggestions):
    exp = re.compile(' {0,}, {0,}')
    return re.sub(exp, ',', suggestions)

#Classe que referencia enquetes e guarda os atributos nome da enquete, proprietário, data final,
#local de reunião, sugestões de horário, quantidade de votos, flag para verificação de enquete
#em andamento e usuários inscritos/votante
@Pyro4.expose
class Poll:
    def __init__(self, title = "", owner = None, dueDate = None, place = "", suggestions = [], opened = True, subscribers = []):
        self.title = title
        self.owner = owner
        self.dueDate = dueDate
        self.place = place
        self.suggestions = suggestions
        self.voteCount = [0] * len(suggestions)
        self.opened = opened     
        self.subscribers = subscribers

    def getTitle(self):
        return self.title
        
    def getSuggestions(self):
        return self.suggestions

    def receiveVote(self, index, subscriber):
        self.subscribers.append(subscriber)
        self.voteCount[index] = self.voteCount[index] + 1

    def closePoll(self):
        if(not self.opened):
            return
        #se a enquete foi encerrada retorna o resultado da sugestão vencedora // em caso de empate escolhe por default aquela com menor índice
        self.opened = False
        winner = self.suggestions[self.voteCount.index(max(self.voteCount))]

        for subscriber in self.subscribers:
            subscriber.getReference().closedPoll(self.title, winner)
        if self.owner not in self.subscribers:
            self.owner.getReference().closedPoll(self.title, winner)

    def getData(self):
        return {
            'name': self.title,
            'voteCount': self.voteCount,
            'suggestions': self.suggestions,
            'opened': self.opened,
            'subscribers': [sub.getName() for sub in self.subscribers]
        }

    #Verifica se o usuário é votante da enquete indicada (self)
    def isSubscriber(self, sub):
        for subscriber in self.subscribers:
            if(subscriber.getUri() == sub):
                return True
        return False
        

#ClientInstance#
#Classe que possibilita a criação de uma instância de cliente dentro do servidor para armazenar
#nome, referência, chave pública e o código identificador do processo cliente (uri)

class ClientInstance:
    def __init__(self, name = "", reference = "", key = "", uri = ""):
        self.name = name
        self.referece = reference
        self.publicKey = key
        self.uri = uri

    def getUri(self):
        return self.uri

    def getName(self):
        return self.name

    def getPubKey(self):
        return self.publicKey

    def getReference(self):
        return self.referece
        

#Server#
#Classe que possibilita instanciar um objeto servidor na main e permite chamadas de métodos
#em processos clientes
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):
    def __init__(self, clients = [], polls = [], startDate = None):
        self.clients = clients
        self.polls = polls
        self.startDate = datetime.now() + timedelta(seconds=15)

    def getUser(self, uri):
        for client in self.clients:
            if client.getUri() == uri:
                return client
        raise Exception('Usuario nao encontrado!')

    def getPoll(self, title):
        for poll in self.polls:
            if poll.getTitle() == title:
                return poll   
        raise Exception('Enquete nao encontrado!')
        
                                                      # coesão e desacoplamento
    def runServer(self):                                    # MÃO DO SIMÃO
        with Pyro4.Daemon() as daemon:                #$$$$$$$$$$$$$$$$$$$$$$$$$
            #registra a aplicação do                  #$$$$$$$$$$$$$$$$$$$' '$$$
            #servidor no serviço de nomes             #$$$$$$$$$$$$$$$$$$$  $$$$  
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
        poll = Poll(title, owner, str2Date(dueDate), place, suggestions)
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

    def checkPoll(self, clientUri, pollName, signature):
        ## hasheia o pollName
        ## verifica com a signature e pubkey se eh valido
        poll = self.getPoll(pollName)
        client = self.getUser(clientUri)
        pk = client.getPubKey()
        pubKey = RSA.construct((pk['n'], pk['e']))
        hash = SHA256.new(pollName.encode('utf-8')).digest()

        if pubKey.verify(hash, signature) and ((poll.owner.uri == clientUri) or (poll.isSubscriber(clientUri))):
            return {
                'error': False,
                'message': 'Deu boa',
                'data': poll.getData()
            }

        return {
            'error': True,
            'message': 'Permissão negada!',
            'data': None
        }

    
#MAIN#
#Instancia o objeto server da classe Server e chama o método que inicializa thread
#do servidor que ficará aguardando requisições de clientes
#Cria e inicializa thread que ficará checando o horário de encerramento da enquete
def main():
    server = Server()

    thread = threading.Thread(target=server.checkDueDate)
    thread.daemon = True
    thread.start()
    
    server.runServer()

main()