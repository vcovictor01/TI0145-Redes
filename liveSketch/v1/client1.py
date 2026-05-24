import socket
import threading

#---------------------------------------------------------------------------------------------

SERVER_IP = 'localhost'  #IP REAL DO SERVIDRO 
PORT = 6666

socketC1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket IPv4 TCP
print(f"* Conectando ao servidor em {SERVER_IP}:{PORT}...")

socketC1.connect((SERVER_IP, PORT))
print("+ Conectado ao servidor")

#---------------------------------------------------------------------------------------------

playerRole = socketC1.recv(1024).decode('utf-8').split(":")[1] #Servidor envia "STATUS:ROLE"

print(f"\n==========================================")
print(f"* VOCÊ ENTROU COMO: {playerRole}")
print(f"==========================================\n")

#---------------------------------------------------------------------------------------------

def receiveServerData(): #Função que recebe mensagens do servidor
    
    while True:
        try:
            data = socketC1.recv(1024).decode('utf-8')
            
            if not data:
                print("\n- O servidor encerrou a sessão.")
                break
                
            print(f"\nm {data}")
            
        except (ConnectionResetError, ConnectionAbortedError):
            print("\n- Conexão com o servidor foi perdida abruptamente.")
            break
        except Exception as e:
            print(f"\ne Falha na recepção: {e}")
            break
            
    print("* Thread de recepção encerrada. Pressione Enter para sair.")
    socketC1.close()

serverReceiverThread = threading.Thread(target=receiveServerData, daemon=True) #daemon=True encerra a thread se o programa fechar
serverReceiverThread.start()

#---------------------------------------------------------------------------------------------

print("* O COMANDO 'sair' ENCERRA A CONEXAO\n")
while True: #Envia mensagens para o servidor
    try:
        msg = input()
        
        if msg.strip().lower() == 'sair':
            print("* Desconectado")
            break
            
        if not msg.strip(): #Não envia mensagens vazias
            continue
            
        socketC1.sendall(msg.encode('utf-8'))
        
    except OSError:
        print("\n[-] Não foi possível enviar. Você foi desconectado.")
        break
    except (KeyboardInterrupt, EOFError):
        # Captura Ctrl+C de forma limpa
        break

# Encerra o socket ao sair do loop
socketC1.close()
print("* Cliente finalizado.")