# chave https://medium.com/@jonathas.mpf/assinatura-digital-com-python-d03df25116fb

import Pyro4
import threading
import sys
from datetime import datetime, timedelta
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

Running = True

menu_message = '\nDigite 1 para cadastrar enquete\nDigite 2 para votar em uma enquete\nDigite 3 para mostrar resultado de enquete'

@Pyro4.expose
@Pyro4.callback
class Client(object):
    @Pyro4.expose
    def notification(self, poll, suggestions):
        print("Nova enquete recebida: " + str(poll))

    def closedPoll(self, pollName, chosenDate):
        print('A enquete ' + pollName + ' foi encerrada!')
        print('A data e horário escolhidos foram: ' + chosenDate)

    def newPoll(self, server, uri):
        # cliente preenche nome, título, local e data da reunião e data limite para votação
        #clientName = input('Digite o nome do cliente: ')
        title = input('Digite o nome da enquete/reunião: ')
        # place = input('Digite o local da reunião: ')
        # suggestions = input('Digite as opções de horário separ dos por vírgula no formato dd/mm/aaaa hh:mm:ss: ')
        # dueDate = input('Digite o prazo para encerramento da enquete no formato dd/mm/aaaa hh:mm:ss: ')
        # chama o método do server passando as informações necessárias para criar nova enquete no servidor
        # server.newPoll(clientName, title, place, suggestions, dueDate)
        server.newPoll(uri, title, 'montanha', '28/10/2021 10:00:00,28/10/2021 11:00:00 , 28/10/2021 12:00:00', datetime.strftime(datetime.now() + timedelta(seconds=50), '%d/%m/%y %H:%M:%S'))
        # server.newPoll(uri, title, place, suggestions, dueDate)

    def loopThread(daemon):
        daemon.requestLoop(lambda: Running)

    def callBackLoopThread(object):
        # thread->requestLoop do callback
        print('callback()')

    def pollVote(self, server, uri):

        title = input('Digite o nome da enquete: ')
        suggestions =  server.getPollSuggestions(title)

        if(suggestions == False):
            print('Não é possível votar. Enquete encerrada.')
            return

        for index, suggestion in enumerate(suggestions):
            print(index + 1, suggestion)

        chosenDate = input('Escolha a melhor data: ')

        server.pollVote(uri, title, chosenDate)

    def checkPoll(self, server, clientUri, keyPair):

        pollName = input('Digite o nome do evento: ')
        #haseia o pollName e gera o digitalSign através do keyPair.sign()

        hashA = SHA256.new(pollName.encode('utf-8')).digest() 
        digitalSign = keyPair.sign(hashA, '') 
        response = server.checkPoll(clientUri, pollName, digitalSign)

        if(response['error']):
            print(response['message'])
            return

        poll = response['data']
        print('Consulta realizada com sucesso!')
        #tá dando cagada nos dados de retorno - tô com sono
        # print('A enquete ', poll.name, ' possuí ', poll.voteCount, ' votos.')


def main():

    # obtém a referência da aplicação do server no serviço de nomes
    ns = Pyro4.locateNS()
    uri = ns.lookup("SearchNameServer")
    server = Pyro4.Proxy(uri)
    # ... server.metodo() —> invoca método no server
    # Inicializa o Pyro daemon e registra o objeto Pyro callback nele.
    #server.test()
    daemon = Pyro4.core.Daemon()
    callback = Client()
    clientUri = daemon.register(callback)
    # loopThread = callback.loopThread
    callback.callBackLoopThread()
    # inicializa a thread para receber notificações do server
    thread = threading.Thread(target=Client.loopThread, args=(daemon,))
    thread.daemon = False
    thread.start()
    userName = input('Nome do usuário: ')

    random_seed = Random.new().read
    keyPair = RSA.generate(1024, random_seed)
    pubKey = keyPair.publickey()

    
    
    server.register(clientUri, userName, pubKey)
    print('Usuário criado: ' + str(userName))
    print(menu_message)
    for line in sys.stdin:
        if 'exit' == line.rstrip():
            global Running
            Running = False
            break
        if '1' == line.rstrip():
            callback.newPoll(server, clientUri)
        if '2' == line.rstrip():
            callback.pollVote(server, clientUri)
        if '3' == line.rstrip():
            callback.checkPoll(server, clientUri, keyPair)
        if '4' == line.rstrip():
            server.getClients()
        print(menu_message)
    print('Exit')

main()