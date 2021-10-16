import Pyro4
import threading
import sys

Running = True

@Pyro4.expose
@Pyro4.callback
class Client(object):

    def notification(self):
        print("callback recebido do server!")   

    def loopThread(daemon):
        # thread para ficar escutando chamadas de método do server
        print('Cliente esperando')
        daemon.requestLoop(lambda: Running)

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
    daemon.register(callback)
    # loopThread = callback.loopThread
    # inicializa a thread para receber notificações do server
    thread = threading.Thread(target=Client.loopThread, args=(daemon,))
    thread.daemon = False
    thread.start()
    for line in sys.stdin:
        if 'exit' == line.rstrip():
            global Running
            Running = False
            break
        print('Digite exit para sair')
    print('Exit')

main()