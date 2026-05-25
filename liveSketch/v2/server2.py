import socket
import threading
import random

#---------------------------------------------------------------------------------------------
#INICIANDO SERVIDOR

HOST = '0.0.0.0'  
PORT = 6666

socketS1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket IPv4 TCP
socketS1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Libera porta 6666 imediatamente

socketS1.bind((HOST, PORT))
socketS1.listen(2)  #Fila de espera para conexão de 2 players
print(f"[SISTEMA] Servidor iniciado na porta {PORT}. Aguardando conexão...\n")

players = [] #Armazena as conexões dos players
role = ["actor", "observer"]

#---------------------------------------------------------------------------------------------
#INICIANDO CONEXÕES

while len(players) < 2: #Loop de conexão para 2 jogadores
    socketC1, address = socketS1.accept()
   
    playerRole = role[len(players)] #Define a role do player: 1 - actor, 2 - observer
    players.append(socketC1)
    
    print(f"[SYSTEM] Jogador {len(players)} [{playerRole}] conectado de {address}.")

    roleMSG = f"STATUS:{playerRole}" #Mensagem contendo a role do player para o client
    socketC1.sendall(roleMSG.encode('utf-8'))

print("\n[SYSTEM] Conexão concluída! Iniciando threads de comunicação.")

#---------------------------------------------------------------------------------------------
#DEFININDO KEY

KEYLIST = ["gato", "carro", "casa", "arvore", "sol", "computador", "garrafa"]
key = random.choice(KEYLIST)
keyMSG = f"NEW_WORD:{key}"
players[0].sendall(keyMSG.encode('utf-8'))

#---------------------------------------------------------------------------------------------

def flowManager(sourceSocket, mainRole, destinationSocket): #Função executada pela thread de ambos clients
    global key
    while True:
        try:
            data = sourceSocket.recv(1024).decode('utf-8')
        
            if not data: 
                break #Conexão encerrada quando não há dados
            
            try: destinationSocket.sendall(data.encode('utf-8'))
            except: pass
            
            #Checa se o dado recebido é a key
            comandos = data.split('\n')
            for comando in comandos:
                if comando.startswith("MSG:"):
                    msg = comando.replace("MSG:", "").strip().lower()
                    
                    if msg == key and mainRole == "observer":
                        pointMSG = f"[SYSTEM] O Jogador acertou a palavra! {key}!\n"
                        clearMSG = "CLEAR\n" #Comando para limpar canva
                        for p in players:
                            p.sendall(pointMSG.encode('utf-8'))
                            p.sendall(clearMSG.encode('utf-8'))
                        
                        key = random.choice(KEYLIST)
                        keyMSG = f"NEW_WORD:{key}\n"
                        players[0].sendall(keyMSG.encode('utf-8'))
                    
                    elif msg == key and mainRole == "actor":
                        strikeMSG = f"[SYSTEM] A MENSAGEM CONTÉM A RESPOSTA\n"
                        players[0].sendall(strikeMSG.encode('utf-8'))
                     
        except (ConnectionResetError, ConnectionAbortedError, OSError): #Conexão encerrada por erro
            break
        except Exception as e:
            print(f"[ERRO] Ocorreu um problema na thread do {mainRole}: {e}")
            break 
                

    print(f"[SYSTEM] Conexão com o {mainRole} foi encerrada.")
    
    try: sourceSocket.close() #Quando um cliente fecha, os dois são encerrados
    except: pass
    try: destinationSocket.close()
    except: pass


#O servidor recebe data de um socket e envia para outro socket
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