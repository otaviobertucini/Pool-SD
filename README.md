# Pool-SD
Trabalho apresentado à disciplina de Sistemas Distribuídos do curso Bacharelado em Sistemas de Informação da Universidade Tecnológica Federal do Paraná (UTFPR)

### DESCRIÇÃO ###

#####ARQUITETURA CLIENTE-SERVIDOR

* Modelo Publisher/Subscriber (Eventos e Notificações)
* Aplicação para agendamento de reuniões em um departamento através de enquetes

Utilizada a middleware PyRO(Python Remote Objects) para prover a comunicação entre processos.

## 📁 Acesso ao projeto

PROJETO DISPONÍVEL EM https://github.com/otaviobertucini/Pool-SD


## 🛠️ Abrir e rodar o projeto
- GARANTA QUE ESTÁ UTILIZANDO UMA VERSÃO PYTHON3 3.6.* OU INFERIOR NO SEU QUERIDO UBUNTU
    	$ python3 --version
- INSTALE O GERENCIADOR DE PACOTES PIP3: 
   	 $ sudo apt install python3-pip
- INSTALE PYRO4:
    	$ pip install Pyro4
- INSTALE A BIBLIOTECA PYCRYPTO: 
    	$ pip install pycrypto
- COM O AMBIENTE CONFIGURADO E O CÓDIGO BAIXADO, EXECUTE:
    	$ python3 -m Pyro4.naming 
- EM OUTRO TERMINAL ABRA O SERVIDOR:
    	$ python3 server.py
- EM OUTRO(S) TERMINAL(IS) ABRA O(S) CLIENTE(S):
    	$ python3 client.py
###### BRINQUE! 
######OBS.: VERSÕES DE PYTHON3 ACIMA DE 3.6.* NÃO RECONHECEM UM MÓDULO(TIME()CLOCK()) DENTRO DA LIB PYCRYPTO E CONSEQUENTEMENTE NÃO FUNCIONA!

### FEATURES

[X] - CADASTRO DE USUÁRIO
[X] - CADASTRO DE ENQUETE
[X] - CADASTRO VOTO ENQUETE
[X] - CONSULTA ENQUETE