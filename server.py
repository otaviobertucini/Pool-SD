import Pyro4

# configura uma instância única do servidor para ser consumida por diversos
# clientes

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class ClientInstance:

    name = ''
    referece = ''
    publicKey = ''

    def __init__(self, name, reference, key):

        self.name = name
        self.referece = reference
        self.publicKey = key
class Server(object):

    clients = []

    #coesão e desacoplamento------------------------       MÃO DO SIMÃO
    def runServer(self):                              #$$$$$$$$$$$$$$$$$$$$$$$$$
        with Pyro4.Daemon() as daemon:                #$$$$$$$$$$$$$$$$$$$' '$$$
#registra a aplicação do servidor no serviço de nomes #$$$$$$$$$$$$$$$$$$$  $$$$
            uri = daemon.register(self)               #$$$$$$$'/ $/ `/ `$' .$$$$
            ns = Pyro4.locateNS()                     #$$$$$$'|. i  i  /! .$$$$$
            ns.register("SearchNameServer", uri)      #$$$$$$$'_'.--'--'  $$$$$$        
            print('uri:', uri)
            print("Server is ready")                  #$$^^$$$$$'        J$$$$$$
            daemon.requestLoop()                      #$$$   ~""   `.   .$$$$$$$
                                                      #$$$$$',      ;  '$$$$$$$$                                                
                                                      #$$$$$$$$$$$.'   $$$$$$$$$

    @Pyro4.expose    

    def test(self):                                 

        print("Não sei de nada")

    @Pyro4.expose
    def register(self, uri, name, key):
        # registra usuário, passa chave e referência do cliente
        print(uri)
        client = Pyro4.Proxy(uri)

        instance = ClientInstance(name, client, key)
        self.clients.append(instance)     

    def poolResquest(self):
        # chamar método do cliente para avisar nova enquete
        print('nada')

    @Pyro4.expose
    def getClients(self):

        for client in self.clients:

            print('oie: ' + client.name)

def main():
    server = Server()
    server.runServer()

main()