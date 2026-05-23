import socket

#IP de loopback local para validar o código.
SERVER_IP = 'localhost' 
PORT = 6666

socketC0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket IPv4 TCP
print(f"[*] Tentando se conectar ao servidor {SERVER_IP}:{PORT}...")

socketC0.connect((SERVER_IP, PORT)) #Conecta ao servidor
print("[+] Conectado ao servidor!")

msg = "Olá, Servidor! Sou o Cliente do SocketSketch."
socketC0.sendall(msg.encode('utf-8')) #Envia mensagem para o servidor
print("[->] Mensagem de teste enviada.")

resposta = socketC0.recv(1024).decode('utf-8') #Agurdando resposta
print(f"[<-] Resposta do servidor: '{resposta}'")
print("[*] Encerrando socket do cliente.")

#Encerra sockets
socketC0.close()