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

menu_message = 'Digite 1 para cadastrar usuário\nDigite 2 para cadastrar nova enquete\nDigite 3 para votar em uma enquete'

@Pyro4.expose
@Pyro4.callback
class Client(object):

    @Pyro4.expose
    def notification(self):
        print("callback recebido do server!")   

    def loopThread(daemon):
        # thread para ficar escutando chamadas de método do server
        print('Menu')
        print(menu_message)
        daemon.requestLoop(lambda: Running)

    def callBackLoopThread(objetc):
        # thread->requestLoop do callback
        print('sei não ehin')

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
    for line in sys.stdin:
        if 'exit' == line.rstrip():
            global Running
            Running = False
            break
        if '2' == line.rstrip():
            pool_name = input('Nome da enquete: ')
            server.register(client_uri, pool_name, None)
            print('Enquete criada: ' + str(pool_name))
        if '3' == line.rstrip():
            server.getClients()
        print(menu_message)
    print('Exit')

main()