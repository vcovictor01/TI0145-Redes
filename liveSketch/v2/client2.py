import socket
import threading
import os 
import tkinter as tk
from tkinter import scrolledtext

#---------------------------------------------------------------------------------------------
#INICIALIZANDO CONEXÃO

SERVER_IP = 'localhost'  #IP REAL DO SERVIDOR
PORT = 6666

socketC1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket IPv4 TCP
socketC1.connect((SERVER_IP, PORT))
print("[SYSTEM] Conectado ao servidor")

playerRole = socketC1.recv(1024).decode('utf-8').split(":")[1] #Recebe do servidor "STATUS:ROLE"


#---------------------------------------------------------------------------------------------
#CONSTRUÇÃO DA INTERFACE

root = tk.Tk()
root.title(f"LiveSketch - Papel: {playerRole.upper()}")
root.geometry("800x500")
root.configure(bg="#333333") #Janela do jogo

pencil = "black" 
pencilSize = 20   #Tamanho do pixel

#CHAT=============================================

    #Janela do chat
frameCHAT = tk.Frame(root, bg="#333333", width=300)
frameCHAT.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    #Título do chat
labelChatTitle = tk.Label(frameCHAT, text="CHAT", fg="white", bg="#333333", font=("Arial", 12, "bold"))
labelChatTitle.pack(anchor="w")
    #Chat efetivo
containerCHAT = scrolledtext.ScrolledText(frameCHAT, state='disabled', height=20, width=35, bg="#222222", fg="white")
containerCHAT.pack(fill=tk.BOTH, expand=True, pady=5)
    #Janela da entrada de mensagens
frameENTRY = tk.Frame(frameCHAT, bg="#333333")
frameENTRY.pack(fill=tk.X)
    #Mensagem
entry = tk.Entry(frameENTRY, bg="#444444", fg="white", insertbackground="white")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)


def sendMessage(event=None): #Função para enviar mensagem
    texto = entry.get()
    if texto.strip():
        socketC1.sendall(f"MSG:{texto}\n".encode('utf-8'))
        
        #Mostra mensagem enviada
        containerCHAT.configure(state='normal')
        containerCHAT.insert(tk.END, f"> {texto}\n")
        containerCHAT.configure(state='disabled')
        containerCHAT.see(tk.END)
        entry.delete(0, tk.END)
 
        
    #Botão de enviar mensagem
entry.bind("<Return>", sendMessage)
btn_enviar = tk.Button(frameCHAT, text="Enviar", command=sendMessage, bg="#555555", fg="white")
btn_enviar.pack(side=tk.RIGHT, padx=5)

#CANVA=============================================

    #Janela do Canva
frameCANVA = tk.Frame(root, bg="#333333")
frameCANVA.pack(side=tk.LEFT, padx=10, pady=10)
    #Texto da key
labelKey = tk.Label(frameCANVA, text="Aguardando Palavra...", fg="yellow", bg="#333333", font=("Arial", 14, "bold"))
labelKey.pack(pady=5)
    #Canva efetivo
canvas = tk.Canvas(frameCANVA, width=400, height=400, bg="white")
canvas.pack()
    
paintedPixels = {}


def paint(event):
    if playerRole == "actor": #Função desenhar apenas para o actor
        
        coluna = event.x // pencilSize
        linha = event.y // pencilSize
        
        if 0 <= coluna < 20 and 0 <= linha < 20:
            tag = f"{coluna},{linha}"
            
            if paintedPixels.get(tag) != pencil:
                paintedPixels[tag] = pencil #Muda a cor do pixel
                bitColor = "1" if pencil == "black" else "0" #1=Preto, 0=Branco
                
                canvas.create_rectangle(coluna*pencilSize, linha*pencilSize, 
                                        (coluna+1)*pencilSize, (linha+1)*pencilSize, 
                                        fill=pencil, outline="#e0e0e0") #Desenha localmente
                
                paintDATA = f"PAINT:{coluna},{linha},{bitColor}\n"
                socketC1.sendall(paintDATA.encode('utf-8')) #Envia qual pixel foi desenhado
         
                
    #Movimento do mouse no canva
canvas.bind("<B1-Motion>", paint)
canvas.bind("<Button-1>", paint)
    #Barra de Ferramentas 
frameTools = tk.Frame(frameCANVA, bg="#333333")
frameTools.pack(fill=tk.X, pady=5)

def pencilSelect(): global pencil; pencil = "black"
def eraseSelect(): global pencil; pencil = "white"
    #Botão de Lápis
btn_lapis = tk.Button(frameTools, text="✏️ Lápis", command=pencilSelect)
btn_lapis.pack(side=tk.LEFT, padx=5)
    #Botão de Borracha
btn_borracha = tk.Button(frameTools, text="🧽 Borracha", command=eraseSelect)
btn_borracha.pack(side=tk.LEFT, padx=5)

if playerRole == "observer":
    frameTools.pack_forget() #Apaga ferramentas para o observer
    labelKey.configure(text="ADIVINHE O DESENHO!", fg="cyan")

#---------------------------------------------------------------------------------------------

def receiveServerData(): #Função que recebe mensagens do servidor
    
    while True:
        try:
            data = socketC1.recv(1024).decode('utf-8')
            
            if not data:
                break
            
            comandos = data.split('\n')
            
            for comando in comandos:
                if not comando.strip(): # Ignora pedaços vazios
                    continue
                
                if comando.startswith("MSG:"): #Mensagens do Chat
                    msg = comando.replace("MSG:", "")
                    containerCHAT.configure(state='normal')
                    containerCHAT.insert(tk.END, f"Jogador: {msg}\n")
                    containerCHAT.configure(state='disabled')
                    containerCHAT.see(tk.END)
                    
                elif comando.startswith("SYSTEM:"): #Mensagens de Sistema
                    sys = comando.replace("SYSTEM:", "")
                    containerCHAT.configure(state='normal')
                    containerCHAT.insert(tk.END, f"[SISTEMA] {sys}\n", "sistema")
                    containerCHAT.tag_config("sistema", foreground="orange", font=("Arial", 10, "bold"))
                    containerCHAT.configure(state='disabled')
                    containerCHAT.see(tk.END)
                    
                elif comando.startswith("NEW_WORD:"): #KEY para o actor
                    palavra = comando.split(":")[1]
                    labelKey.configure(text=f"{palavra.upper()}")
                    
                elif comando.startswith("PAINT:"): #Desenho Remoto para o observer
                    pt = comando.split(":")[1].split(",")
                    col = int(pt[0])
                    lin = int(pt[1]) #Divide o dado de desenhar em três parte (pixelcol, pixellin, color)
                    color = "black" if pt[2] == "1" else "white"
                    
                    canvas.create_rectangle(col*pencilSize, lin*pencilSize, 
                                            (col+1)*pencilSize, (lin+1)*pencilSize, 
                                            fill=color, outline="#e0e0e0")
                
                # Comando de limpar a tela após acerto
                elif comando == "CLEAR":
                    canvas.delete("all")
                    paintedPixels.clear()
            
        except:
            break
            
    print("[SYSTEM] Desconectado do servidor.")
    os._exit(0)

serverReceiverThread = threading.Thread(target=receiveServerData, daemon=True) #daemon=True encerra a thread se o programa fechar
serverReceiverThread.start()

#---------------------------------------------------------------------------------------------

root.mainloop()

# Encerra o socket ao sair do loop
try: socketC1.close()
except: pass