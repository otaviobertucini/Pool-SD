import Pyro4
import threading

@Pyro4.expose
@Pyro4.callback
class Client(object):

    def notification(self):
        print("callback recebido do server!")
        
def loopThread(daemon):
    # thread para ficar escutando chamadas de método do server
    print('iajsdndjuisnadjuiabsnjidbas')
    daemon.requestLoop()

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
    thread = threading.Thread(target=loopThread, args=(daemon,))
    thread.daemon = True
    thread.start()

main()