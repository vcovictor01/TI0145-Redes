import socket

HOST = '0.0.0.0'
PORT = 6666

socketS0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket IPv4 TCP
socketS0.bind((HOST, PORT))

socketS0.listen(1) #Escutando
print(f"* Servidor rodando na porta {PORT}.")
print("* Aguardando conexão do cliente...")

socketC0, clientAddress = socketS0.accept() #Dados do cliente pelo socket
print(f"+ Conexão estabelecida com: {clientAddress}")

msgA = socketC0.recv(1024).decode('utf-8') #Mensagem recebida do cliente
print(f"r Mensagem do cliente: '{msgA}'")

msgB = "Conexão confirmada!"
socketC0.sendall(msgB.encode('utf-8')) #Envia mensagem pro cliente
print("e Confirmação enviada. Fechando conexões.")

#Encerra sockets
socketS0.close()
socketC0.close()