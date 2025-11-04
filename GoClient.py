# cliente.py
import Pyro5.api
import time # Usado para time.sleep(), uma pausa para não sobrecarregar o servidor
import os # Para limpar a tela

def limpar_tela():
    """Limpa o console para redesenhar o tabuleiro."""
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_tabuleiro_local(estado):
    """Desenha o tabuleiro no console do cliente."""
    tabuleiro = estado['tabuleiro'] # Ela itera pelo... e converte os números (0, 1, 2) em caracteres (., X, 0)
    tamanho = len(tabuleiro)
    
    jogador = "Preto (X)" if estado['jogador_atual'] == 1 else "Branco (O)"
    
    limpar_tela()
    print("--- Jogo de Go Distribuído (9x9) ---")
    print(f"Vez de: {jogador}\n")
    
    # Cabeçalho (colunas)
    print("  " + " ".join([str(i) for i in range(tamanho)])) # imprimir os npumeros da coluna (0...8)
    # i: O índice da linha (0, 1, 2, ...)
    # linhas: A lista que representa aquela linha (ex: [0, 1, 0, 2])
    for i, linha in enumerate(tabuleiro): # Percorrer cada linha da matriz tabuleiro
        linha_str = f"{i} " # i é a variável que guarda o número da linha atual (0, 1, 2, 3...)
        for celula in linha:
            if celula == 0: linha_str += ". " # Vazio
            elif celula == 1: linha_str += "X " # Preto
            else: linha_str += "O " # Branco
        print(linha_str)
        
    print("\n------------------------------------")
    print(f"Capturadas por Preto (P1): {estado['capturadas_p1']}")
    print(f"Capturadas por Branco (P2): {estado['capturadas_p2']}")
    print("------------------------------------")


# --- Lógica Principal do Cliente ---

# Conectando-se ao Servidor
try:
    # 1. Encontra o "cartório" e pede o "telefone" do objeto "meu.jogo.go"
    servidor_go = Pyro5.api.Proxy("PYRONAME:meu.jogo.go")  # cria um "objeto de proxy" local
except Pyro5.errors.NamingError:
    print("Erro: Não consegui encontrar o servidor.")
    print("Você lembrou de rodar o 'pyro5-ns' (cartório) e o 'servidor.py'?")
    exit()

# 2. Tenta se conectar ao jogo
meu_id_jogador = servidor_go.conectar()
'''A Primeira Chamada RMI: empacota a chamada SG, envia pela rede, o servidor real executa o método Conect()
e retorna um número (1, 2 ou 0)'''

if meu_id_jogador == 0:
    print("O jogo já está cheio. Tente mais tarde.")
    exit()

print(f"Você conectou! Você é o Jogador {meu_id_jogador} ({'Preto (X)' if meu_id_jogador == 1 else 'Branco (O)'})")
print("Esperando o outro jogador...")

estado_anterior = None
ultimo_erro = ""

# 3. Loop principal do jogo
while True:
    try:
        # Pega o estado atualizado do jogo (CHAMADA RMI!)
        estado_atual = servidor_go.get_estado_jogo() # cada seg o cliente "pergunta" ao servidor: "Qual é o estado do jogo agora?"

        # --- LÓGICA DE REDESENHAR (Eficiência)---
        # Agora, redesenhamos se o estado mudou OU se temos um erro.
        if estado_atual != estado_anterior or ultimo_erro: # Isso impede que a tela fique "piscando"
            imprimir_tabuleiro_local(estado_atual) # Desenha o tabuleiro
            
            # Se houver um erro da jogada anterior, mostre-o
            if ultimo_erro:
                print(f"\n!!! JOGADA INVÁLIDA: {ultimo_erro} !!!")
                print("Por favor, tente novamente.")
                ultimo_erro = "" # Limpa o erro
            
            estado_anterior = estado_atual # Atualiza o estado

        # Verifica se o jogo acabou
        if estado_atual['fim_de_jogo']:
            print("FIM DE JOGO! Ambos os jogadores passaram a vez.")
            break

        # É a minha vez de jogar?
        if estado_atual['jogador_atual'] == meu_id_jogador:
            jogada_str = input("Sua vez. Digite 'x,y' (ex: 3,4) ou 'passar': ")
            
            if jogada_str.lower() == 'passar':
                # Chama o método RMI "passar_vez"
                sucesso, msg = servidor_go.passar_vez(meu_id_jogador)
                if not sucesso:
                    ultimo_erro = msg # Armazena o erro
            
            else:
                # Tenta fazer a jogada
                try:
                    x, y = map(int, jogada_str.split(','))
                    # Chama o método RMI "fazer_jogada"
                    sucesso, msg = servidor_go.fazer_jogada(meu_id_jogador, x, y)
                    
                    if not sucesso:
                        ultimo_erro = msg # Armazena o erro
                except ValueError:
                    ultimo_erro = "Formato inválido. Use 'x,y'."
                except Exception as e:
                    ultimo_erro = f"Erro inesperado: {e}"
            
            # não há 'time.sleep' aqui, 
            #  para que o loop rode de novo imediatamente e mostre o erro)

        else:
            # Não é minha vez, espera um pouco antes de verificar de novo polling (Sondagem).
            print("Aguardando jogada do oponente...")
            time.sleep(1.0) # Espera 1 segundo

    except Pyro5.errors.CommunicationError:
        print("\nErro: Conexão com o servidor perdida.")
        break
    except KeyboardInterrupt:
        print("\nSaindo do jogo.")
        break