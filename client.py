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
        title = input('Digite o nome da enquete/reunião: ')
        place = input('Digite o local da reunião: ')
        suggestions = input('Digite as opções de horário separ dos por vírgula no formato dd/mm/aaaa hh:mm:ss: ')
        dueDate = input('Digite o prazo para encerramento da enquete no formato dd/mm/aaaa hh:mm:ss: ')
        try:
            server.newPoll(uri, title, place, suggestions, dueDate)
        except:
            print('Alguma coisa deu errado, tente novamente:')
            return

    def loopThread(daemon):
        daemon.requestLoop(lambda: Running)

    def pollVote(self, server, uri):

        title = input('Digite o nome da enquete: ')
        try:
            suggestions =  server.getPollSuggestions(title)
        except:
            print('Alguma coisa deu errado, tente novamente:')
            return

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

        try:
            response = server.checkPoll(clientUri, pollName, digitalSign)
        except:
            print('Alguma coisa deu errado, tente novamente:')
            return

        if(response['error']):
            print(response['message'])
            return

        poll = response['data']
        print('Consulta realizada com sucesso!')
    
        print('A enquete ', poll['name'], ' possuí ', sum(poll['voteCount']), ' votos.')
        if(poll['opened']):
            print('Enquete em andamento.')
        else:
            print('Enquete encerrada.')
        print('Relação de votos: ')
        for index, suggestion in enumerate(poll['suggestions']):
            print(suggestion + ' tem ' + str(poll['voteCount'][index]) + ' votos.')
        print('Usuários inscritos/votantes: ')
        for sub in poll['subscribers']:
            print(' - ' + sub)



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
    # inicializa a thread para receber notificações do server
    thread = threading.Thread(target=Client.loopThread, args=(daemon,))
    thread.daemon = False
    thread.start()
    userName = input('Nome do usuário: ')

    ## gera as chave privada e pública do cliente
    random_seed = Random.new().read
    keyPair = RSA.generate(1024, random_seed)
    pubKey = keyPair.publickey()    
    
    ## envia a uri, nome e chave pública para o servidor
    server.register(clientUri, userName, pubKey)
    print('Usuário criado: ' + str(userName))
    print(menu_message)
    ## aguarda as entradas do usuário
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