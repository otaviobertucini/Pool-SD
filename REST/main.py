import re
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import uvicorn
from sh import tail
import time
import subprocess
import select

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

        # envia mensagem aos inscritos/interessados o encerramento e resultado da enquete
        for subscriber in self.subscribers:
            subscriber.getReference().closedPoll(self.title, winner)
        # se o proprietário não votou na própria enquete informa o resultado a partir da condição a seguir
        if self.owner not in self.subscribers:
            self.owner.getReference().closedPoll(self.title, winner)

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
    
    # def getClientName():
        


class Server(object):
    def __init__(self, clients=[], polls=[], startDate=None, redis = None):
        self.clients = clients
        self.polls = polls
        self.startDate = datetime.now() + timedelta(seconds=15)
        self.redis = redis

    def getClientsNumber(self):

        return len(self.clients)

    def getUser(self, name):
        for client in self.clients:
            if client.name == name:
                return client
        raise Exception('Usuario nao encontrado!')

    def getPoll(self, title):
        for poll in self.polls:
            if poll.getTitle() == title:
                return poll
        raise Exception('Enquete nao encontrado!')

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
            'event': 'new_event',
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

        if(poll.opened):
            return poll.getSuggestions()
        return False

    def register(self, name):
        instance = ClientInstance(name)
        # coloca o usuário na lista de usuários inscritos no servidor
        self.clients.append(instance)
        self.redis.append({
            'event': 'register',
            'data': {
                'name': name
            }
        })
        print('Usuário ' + name + ' criado com sucesso!')

    def pollVote(self, uri, title, chosenDate):
        user = self.getUser(uri)
        poll = self.getPoll(title)

        if(not poll.opened):
            print('Enquete encerrada!')
            return

        index = int(chosenDate) - 1
        poll.receiveVote(index, user)
        print('O usuário ' + user.getName() + ' votou na enquete ' +
              title + ' escolhendo: ' + poll.suggestions[index])

        # verifica se todos já votaram para encerrar a enquete (total -1 porque o proprietário não vota)
        if(sum(poll.voteCount) == len(self.clients)-1):
            poll.closePoll()

    # Método chamado na thread para verificar data/horário de encerramento e encerrar enquete quando necessário
    def checkDueDate(self):
        while True:
            for poll in self.polls:
                if(datetime.now() >= poll.dueDate):
                    if(poll.opened):
                        poll.closePoll()

    def checkPoll(self, username, pollName):
        poll = self.getPoll(pollName)

        if poll.isSubscriber(username):
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

class Redis:

    def __init__(self, filename):
        
        self.filename = filename
        self.last_message = None
        self.sent_count = 0

    def pop(self, server: Server):

        data = None
        if(self.last_message is None):
            with open(self.filename, "r") as file_read:

                self.last_message = file_read.readlines()[-1]

                if('tombstone' in self.last_message):
                    
                    self.last_message = None

                    return None

        self.sent_count += 1
        data = self.last_message

        print('qq deu')
        print(server.getClientsNumber())
        print(self.sent_count)

        if(self.sent_count >= server.getClientsNumber()):
            self.last_message = None

            self.sent_count = 0

            with open(self.filename, "a") as file_write:

                file_write.write("tombstone\n")

        return data


    def append(self, data):

        with open(self.filename, "a") as file:
            file.write(str(data) + '\n')


app = FastAPI()


hostName = "localhost"
serverPort = 8001

redis = Redis('redis.txt')
server = Server(redis=redis)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logs = []

async def status_event_generator(request):
    
    while True:

        if await request.is_disconnected():
            print('disconected')

        data = redis.pop(server)

        if(not data is None):

            yield {
                "event": "new",
                "data" : str(data)
            }

        await asyncio.sleep(2)


@app.get("/poll/user")
def getUsers(request:Request):
    return server.getUser()

@app.get("/poll")
async def read_root(request: Request):
    asyncio.set_event_loop(asyncio.new_event_loop())
    event_generator = status_event_generator(request)
    return EventSourceResponse(event_generator)


@app.post("/poll")
async def clientSubscribe(request: Request):
    data = await request.json()
    name = data['name']

    server.register(name)
    return name

@app.post("/event")
async def addEvent(request: Request):
    data = await request.json()
    username = data['username']
    name = data['name']
    place = data['place']
    suggestions = data['suggestions']
    due_date = data['due_date']

    server.newPoll(username, name, place, suggestions, due_date)
    return name

@app.post("/details")
async def addEvent(request: Request):
    data = await request.json()
    username = data['username']
    name = data['name']
    
    return server.checkPoll(username, name)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)