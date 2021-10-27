import Pyro4

# configura uma instância única do servidor para ser consumida por diversos
# clientes

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")


class Poll:

    title = ''
    owner = None
    dueDate = ''
    place = ''
    suggestions = []

    def __init__(self, title, owner, dueDate, place, suggestions):

        self.title = title
        self.owner = owner
        self.dueDate = dueDate
        self.place = place
        self.suggestions = suggestions

class ClientInstance:

    name = ''
    referece = ''
    publicKey = ''

    def __init__(self, name, reference, key):

        self.name = name
        self.referece = reference
        self.publicKey = key

    def getName(self):
        return self.name

    def getReference(self):
        return self.referece
class Server(object):

    clients = []
    polls = []

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
    def newPoll(self, clientName, title, place, suggestions, dueDate):
        
        print('cheguei1')
        owner = None
        for client in self.clients:

            if client.getName() == clientName:
                owner = client
                break
        
        
        if owner is None:
            print('Usuário não encontrado!')
            return


        poll = Poll(title, owner, dueDate, place, suggestions.replace(' ', '').split(','))
        print('cheguei2')
        self.polls.append(poll)

        print(self.clients)
        for client in self.clients:
            client.getReference().notification(title, suggestions.replace(' ', '').split(','))

        print('saiu do forzão')

    @Pyro4.expose
    def test(self):                                 

        print("Não sei de nada")

    @Pyro4.expose
    def register(self, uri, name, key):
        # registra usuário, passa chave e referência do cliente
        client = Pyro4.Proxy(uri)

        instance = ClientInstance(name, client, key)
        self.clients.append(instance)    

        print('Usuário ' + name + ' criado com sucesso!') 

    def pollResquest(self):
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