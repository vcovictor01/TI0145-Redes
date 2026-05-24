import socket
import threading

#---------------------------------------------------------------------------------------------

HOST = '0.0.0.0'  
PORT = 6666

socketS1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketS1.bind((HOST, PORT))
socketS1.listen(2)  #Fila de espera para conexão de 2 players

print(f"* Servidor iniciado na porta {PORT}.")
print("* Aguardando a conexão dos dois jogadores.\n")

players = [] #Armazena as conexões dos players
role = ["actor", "observer"]

#---------------------------------------------------------------------------------------------

while len(players) < 2: #Loop de conexão para 2 jogadores
    socketC1, address = socketS1.accept()
   
    playerRole = role[len(players)] #Define a role do player: 1 - actor, 2 - observer
    players.append(socketC1)
    
    print(f"+ Jogador {len(players)} conectado de {address} -> Papel: {playerRole}")

    roleMSG = f"STATUS:{playerRole}" #Mensagem contendo a role do player para o client
    socketC1.sendall(roleMSG.encode('utf-8'))

print("\n* Ambos os jogadores se conectaram! Iniciando as Threads de comunicação...")

#---------------------------------------------------------------------------------------------

def flowManager(sourceSocket, mainRole, destinationSocket): #Função executada pela thread de ambos clients
    
    while True:
        try:
            data = sourceSocket.recv(1024)
        
            if not data: 
                break #Conexão encerrada quando não há dados
                
            destinationSocket.sendall(data) #Repassa os dados recebidos do source para o destination
            
        except ConnectionResetError: #Conexão encerrada por erro
            break
        except Exception as e:
            print(f"[ERRO] Ocorreu um problema na thread do {mainRole}: {e}")
            break 

    print(f"[-] Conexão com o {mainRole} foi encerrada.")
    sourceSocket.close()

#---------------------------------------------------------------------------------------------

actorThread = threading.Thread(
    target=flowManager, 
    args=(players[0], "actor", players[1])
#Chama o repasse de dados: source - actor (client 1) para destination - observer (client 2)
)

observerThread = threading.Thread(
    target=flowManager, 
    args=(players[1], "observer", players[0])
#Chama o repasse de dados: source - observer (client 2) para destination - actor (client 1)
)

actorThread.start() #Inicia Threads
observerThread.start()

#---------------------------------------------------------------------------------------------

#Encerra socket do server
socketS1.close()