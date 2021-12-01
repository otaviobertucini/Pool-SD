import re
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, APIRouter, params
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import uvicorn
# from sh import tail
import time
import subprocess
import select
import threading
import json

# formata o string para datetime no modelo descrito
def str2Date(date):
    return datetime.strptime(date, '%d/%m/%Y %H:%M:%S')

# garante que não haja espaços excedentes na string
def parseSuggestions(suggestions):
    exp = re.compile(' {0,}, {0,}')
    return re.sub(exp, ',', suggestions)

# Classe que referencia enquetes e guarda os atributos nome da enquete, proprietário, data final,
# local de reunião, sugestões de horário, quantidade de votos, flag para verificação de enquete
# em andamento e usuários inscritos/votante
class Poll:
    def __init__(self, title="", owner=None, dueDate=None, place="", suggestions=[], opened=True, subscribers=[]):
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

    def getOwner(self):
        return self.owner

    def getSuggestions(self):
        return self.suggestions

    def receiveVote(self, index, subscriber):
        # ao votar o usuário é inscrito na lista de votantes/interessados na enquete
        self.subscribers.append(subscriber)
        # incrementa o voto para a opção selecionada
        self.voteCount[index] = self.voteCount[index] + 1

    def closePoll(self):
        # se a enquete já foi encerrada retorna
        if(not self.opened):
            return
        # Encerra a enquete e define a opçao vencedora// em caso de empate escolhe por default aquela com menor índice
        self.opened = False
        winner = self.suggestions[self.voteCount.index(max(self.voteCount))]

        redis.append({
            'type': 'closedPoll',
            'data': {
                'message': 'Enquete ' + self.title + ' encerrada. Horário escolhido foi ' + winner + ' com ' + str(max(self.voteCount)) + ' votos.'
            }
        })

    # Método para retornar dados de consulta de enquete: nome da enquete, quantidade de votos, sugestões, condição(aberta ou encerrada) e inscritos/interessados
    def getData(self):
        return {
            'name': self.title,
            'voteCount': self.voteCount,
            'suggestions': self.suggestions,
            'opened': self.opened,
            'subscribers': [sub.getName() for sub in self.subscribers]
        }

    # Verifica se o usuário é votante da enquete indicada (self)
    def isSubscriber(self, sub):
        for subscriber in self.subscribers:
            if(subscriber.name == sub):
                return True
        return False


#ClientInstance#
# Classe que possibilita a criação de uma instância de cliente dentro do servidor para armazenar
# nome, referência, chave pública e o código identificador do processo cliente (uri)
class ClientInstance:
    def __init__(self, name="", reference=""):
        self.name = name
        self.referece = reference

    def getName(self):
        return self.name


class Server(object):
    def __init__(self, clients=[], polls=[], startDate=None, redis=None):
        self.clients = clients
        self.polls = polls
        self.startDate = datetime.now() + timedelta(seconds=12)
        self.redis = redis

    def getClientsNumber(self):

        return len(self.clients)

    def removeUser(self, username):

        user = self.getUser(username)

        self.clients.remove(user)

        return self.clients

    def getUser(self, name):
        for client in self.clients:
            if client.name == name:
                return client
        raise Exception('Usuario nao encontrado!')

    def getPoll(self, title):
        for poll in self.polls:
            if poll.getTitle() == title:
                return poll
        # raise Exception('Enquete nao encontrado!')
        return 'erro'
        
        # MÃO DO SIMÃO
    # coesão e desacoplamento
    # $$$$$$$$$$$$$$$$$$$$$$$$$
    # $$$$$$$$$$$$$$$$$$$' '$$$
    # $$$$$$$$$$$$$$$$$$$  $$$$
    # $$$$$$$'/ $/ `/ `$' .$$$$
    # $$$$$$'|. i  i  /! .$$$$$
    # $$$$$$$'_'.--'--'  $$$$$$
    # $$^^$$$$$'        J$$$$$$
    # $$$   ~""   `.   .$$$$$$$
    # $$$$$',      ;  '$$$$$$$$
    # $$$$$$$$$$$.'   $$$$$$$$$

    def newPoll(self, username, title, place, suggestions, dueDate):
        owner = self.getUser(username)
        suggestions = parseSuggestions(suggestions).split(',')
        poll = Poll(title, owner, str2Date(dueDate), place, suggestions)
        self.polls.append(poll)

        redis.append({
            'type': 'new_event',
            'data': {
                'username': username,
                'name': title,
                'place': place,
                'suggestions': suggestions,
                'dueDate': dueDate
            }
        })

    def getPollSuggestions(self, title):
        poll = self.getPoll(title)
          
        if(poll == 'erro'):
            return{
                'error': True,
                'message': 'Enquete enquete não existe'
            }

        elif(poll.opened):
            return {
                'error': False,
                'data': poll.getSuggestions()
            }
        return {
            'error': True,
            'message': 'Enquete encerrada'
        }

    def register(self, name):
        instance = ClientInstance(name)
        # coloca o usuário na lista de usuários inscritos no servidor
        self.clients.append(instance)
        self.redis.append({
            'type': 'register',
            'data': {
                'name': name
            }
        })
        print('Usuário ' + name + ' criado com sucesso!')

    def pollVote(self, username, title, chosenDate):
        user = self.getUser(username)
        poll = self.getPoll(title)

        # verifica se o usuário é o dono da enquete e proíbe a votação
        if(poll.owner == user):
            return {
                'error': True,
                'message': 'Dono não pode votar!',
            }

        # verifica se o usuário já votou na enquete e proíbe a votação
        if(poll.isSubscriber(user.getName())):
            return{
                'error': True,
                'message': 'Usuário ' + user.getName() + ' já votou'
            }
        
        # verifica se a enquete foi fechada e proíbe a votação
        if(not poll.opened):
            print('Enquete encerrada!')
            return

        index = int(chosenDate) - 1
        poll.receiveVote(index, user)
        print('O usuário ' + user.getName() + ' votou na enquete ' +
              title + ' escolhendo: ' + poll.suggestions[index])

        # verifica número de votos, se for igual ao número de inscritos encerra a enquete
        if(sum(poll.voteCount) == len(self.clients) - 1):
            poll.closePoll()

        return {
            'error': False,
            'message': 'Voto cadastrado com sucesso!'
        }

    # Método chamado na thread para verificar data/horário de encerramento e encerrar enquete quando necessário
    def checkDueDate(self):
        while True:
            for poll in self.polls:
                if(datetime.now() >= poll.dueDate):
                    if(poll.opened):
                        poll.closePoll()

    def checkPoll(self, username, pollName):
        poll = self.getPoll(pollName)

        if(poll == 'erro'):
            return {
                'error': True,
                'message': 'Enquete não existe'
            }
        if (poll.isSubscriber(username) or poll.getOwner().name == username):           
            return {
                'error': False,
                'message': 'Deu boa',
                'data': poll.getData()
            }
        return {
            'error': True,
            'message': 'Permissão negada! Usuário ' + username + ' não cadastrado na enquete.',
            'data': None
        }

# Classe de simulação de banco -> REDIS (fila -> FIFO)
class Redis:

    # construtor
    def __init__(self, filename):

        self.filename = filename
        self.last_message = None
        self.sent_count = 0

    # lê a última mensagem que está na vez de ser lida
    def pop(self, server: Server):

        data = None
        if(self.last_message is None):
            with open(self.filename, "r") as file_read:

                self.last_message = file_read.readlines()[-1]

                if('tombstone' in self.last_message):

                    self.last_message = None

                    return None

        # contador de mensagens enviadas/notificações
        self.sent_count += 1
        data = self.last_message

        # checa o número de notificações e encerra o envio quando for >= número de inscritos
        if(self.sent_count >= server.getClientsNumber()):
            self.last_message = None

            self.sent_count = 0

            with open(self.filename, "a") as file_write:
                # indica o final do arquivo -> não há novas mensagens
                file_write.write("tombstone\n")

        return data

    # adiciona mensagens à fila no REDIS
    def append(self, data):

        with open(self.filename, "a") as file:
            file.write(json.dumps(data) + '\n')


app = FastAPI()

hostName = "localhost"
serverPort = 8001

redis = Redis('redis.txt')
server = Server(redis=redis)

# Diz pro servidor que são aceitos qualquer origem, qualquer método e qualquer cabeçalho(header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# método que 'escuta/lê' o REDIS intermitentemente 
async def status_event_generator(request, username):

    while True:

        data = redis.pop(server)

        if(not data is None):

            yield {
                "event": username,
                "data": str(data).replace('\n', '')
            }

        await asyncio.sleep(0.1)



# Rotas para as chamadas de api #

@app.get("/poll/{user}")
def getUser(request: Request):
    return server.getUser(request.path_params['user'])

# Inicializa o SSE do starlete.sse -> EvenSourceResponse
# utilizar o publish do sse do python
@app.get("/poll")
async def read_root(request: Request, username: str):
    asyncio.set_event_loop(asyncio.new_event_loop())
    event_generator = status_event_generator(request, username)
    return EventSourceResponse(event_generator)

# Registrar um novo cliente
@app.post("/client")
async def clientSubscribe(request: Request):
    data = await request.json()
    name = data['name']

    server.register(name)
    return data

# Registrar nova enquete
@app.post("/event")
async def addEvent(request: Request):
    data = await request.json()
    username = data['username']
    name = data['name']
    place = data['place']
    suggestions = data['suggestions']
    due_date = data['due_date']

    server.newPoll(username, name, place, suggestions, due_date)
    return data

# Registrar novo voto
@app.post("/vote")
async def addEvent(request: Request):
    data = await request.json()
    username = data['username']
    name = data['name']
    date = data['chosenDate']

    response = server.pollVote(username, name, date)
    return response

# Acessar detalhes da enquete
@app.get("/details")
async def checkEvent(username: str, name: str):

    return server.checkPoll(username, name)

# Acessar sugestões de horário para votação em determinada enquete
@app.get("/suggestions")
async def checkEvent(name: str):

    return server.getPollSuggestions(name)

# Retirar usuário da lista (receber mensagens/notoficações em cada novo evento) quando o navegador é fechado
@app.post("/close")
async def checkEvent(username: str):

    print('CLOSED FOR ' + str(username))

    server.removeUser(username)

    return True

if __name__ == "__main__":

    thread = threading.Thread(target=server.checkDueDate)
    thread.daemon = True
    thread.start()

    uvicorn.run(app, port=8000)
