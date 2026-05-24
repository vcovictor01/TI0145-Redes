import socket
import threading
import sys

# Configuração de conexão
SERVER_IP = '127.0.0.1'  # Altere para o IP real do servidor quando testar em 2 PCs
PORT = 6060

# 1. Criação e conexão do socket do cliente
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"[*] Conectando ao servidor SocketSketch em {SERVER_IP}:{PORT}...")
try:
    socket_cliente.connect((SERVER_IP, PORT))
    print("[+] Conexão estabelecida!")
except ConnectionRefusedError:
    print("[ERRO] Não foi possível conectar. O servidor está ligado?")
    sys.exit()

# 2. Fase de Handshake da Aplicação (Descobrir o papel)
# O cliente obrigatoriamente espera o servidor dizer se ele é Desenhista ou Adivinhador
dados_iniciais = socket_cliente.recv(1024).decode('utf-8')
if dados_iniciais.startswith("STATUS:"):
    meu_papel = dados_iniciais.split(":")[1]
    print(f"\n==========================================")
    print(f" VOCÊ ENTROU COMO: {meu_papel}")
    print(f"==========================================\n")

# 3. Thread de Recepção (Ouvindo o Servidor em Background)
def escutar_servidor():
    """
    Função executada em paralelo. Fica em um loop infinito dando recv()
    para capturar tudo o que o servidor repassar do outro jogador.
    """
    while True:
        try:
            # Fica bloqueado aqui até chegar algo da rede
            dados_recebidos = socket_cliente.recv(1024).decode('utf-8')
            
            if not dados_recebidos:
                # Se o servidor fechar a conexão de forma limpa
                print("\n[-] O servidor encerrou a sessão.")
                break
                
            # Exibe a mensagem que veio do outro jogador através do servidor
            print(f"\n[Mensagem Remota]: {dados_recebidos}")
            
        except (ConnectionResetError, ConnectionAbortedError):
            print("\n[-] Conexão com o servidor foi perdida abruptamente.")
            break
        except Exception as e:
            print(f"\n[ERRO] Falha na recepção: {e}")
            break
            
    print("[*] Thread de recepção encerrada. Pressione Enter para sair.")
    socket_cliente.close()

# Dispara a thread de recepção antes de entrar no loop de envio
# daemon=True garante que a thread morra se o programa principal fechar
thread_receber = threading.Thread(target=escultar_servidor, daemon=True)
thread_receber.start()

# 4. Loop Principal de Envio (Fluxo do Teclado)
print("[*] Digite suas mensagens abaixo para enviar ao outro jogador (ou 'sair'):\n")
while True:
    try:
        # O input() bloqueia a thread principal até você dar Enter
        mensagem = input()
        
        if mensagem.strip().lower() == 'sair':
            print("[*] Desconectando...")
            break
            
        if not mensagem.strip():
            continue
            
        # Envia a string convertida em bytes pelo socket puro
        socket_cliente.sendall(mensagem.encode('utf-8'))
        
    except (KeyboardInterrupt, EOFError):
        # Captura Ctrl+C de forma limpa
        break

# Encerra o socket ao sair do loop
socket_cliente.close()
print("[*] Cliente finalizado.")