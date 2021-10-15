import Pyro4

# configura uma instância única do servidor para ser consumida por diversos
# clientes

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):

    def test(self):

        print("Não sei de nada")

def main():
    # registra a aplicação do servidor no serviço de nomes
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Server)
    ns.register("SearchNameServer", uri)
    print("A aplicacao esta ativa")
    daemon.requestLoop()

main()