import Pyro4
import threading
import sys

# chave https://medium.com/@jonathas.mpf/assinatura-digital-com-python-d03df25116fb
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
# from Crypto import Random

Running = True
# random_seed = Random.new().read
# keyPair = RSA.generate(1024, random_seed)
# pubKey = keyPair.publickey()

menu_message = '\nDigite 1 para cadastrar enquete\nDigite 2 para votar em uma enquete\nDigite 3 para mostrar resultado de enquete'

@Pyro4.expose
@Pyro4.callback
class Client(object):

    @Pyro4.expose
    def notification(self, poll, suggestions):
        print("Nova enquete recebida: " + str(poll))


    def newPoll(self, server, userName):
        # cliente preenche nome, título, local e data da reunião e data limite para votação
        # clientName = input('Digite o nome do cliente: ')
        title = input('Digite o nome da enquete/reunião: ')
        place = input('Digite o local da reunião: ')
        suggestions = input('Digite as opções de horário separ dos por vírgula no formato dd/mm/aaaa hh:mm:ss: ')
        dueDate = input('Digite o prazo para encerramento da enquete no formato dd/mm/aaaa hh:mm:ss: ')
        # chama o método do server passando as informações necessárias para criar nova enquete no servidor
        # server.newPoll(clientName, title, place, suggestions, dueDate)
        server.newPoll(userName, 'hu3', 'montanha', '26/10/2021 10:00', '26/10/2021 21:00')

    def loopThread(daemon):
        # thread para ficar escutando chamadas de método do server
        # print('Menu')
        # print(menu_message)
        # print('aisjdiasjdj')
        daemon.requestLoop(lambda: Running)

    def callBackLoopThread(objetc):
        # thread->requestLoop do callback
        print('callback()')

def main():

    # obtém a referência da aplicação do server no serviço de nomes
    ns = Pyro4.locateNS()
    uri = ns.lookup("SearchNameServer")
    server = Pyro4.Proxy(uri)
    # ... server.metodo() —> invoca método no server
    # Inicializa o Pyro daemon e registra o objeto Pyro callback nele.
    server.test()
    daemon = Pyro4.core.Daemon()
    callback = Client()
    client_uri = daemon.register(callback)
    # loopThread = callback.loopThread
    callback.callBackLoopThread()
    # inicializa a thread para receber notificações do server
    thread = threading.Thread(target=Client.loopThread, args=(daemon,))
    thread.daemon = False
    thread.start()
    userName = input('Nome do usuário: ')
    server.register(client_uri, userName, None)
    print('Usuário criado: ' + str(userName))
    print(menu_message)
    for line in sys.stdin:
        if 'exit' == line.rstrip():
            global Running
            Running = False
            break
        if '1' == line.rstrip():
            callback.newPoll(server)
        if '2' == line.rstrip():
            pass
        if '3' == line.rstrip():
            pass
        if '4' == line.rstrip():
            server.getClients()
        print(menu_message)
    print('Exit')

main()