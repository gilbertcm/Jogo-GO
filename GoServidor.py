# servidor.py
import Pyro5.api # Importa todas as ferramentas necessárias do Pyro5
from GoGame import JogoGo # Importa a classe

# o Pyro não permite que clientes acessem nenhum objeto remotamente
# @Pyro5.api.expose diz ao Pyro: "Este objeto pode ser acessado remotamente"
@Pyro5.api.expose
class ServidorJogo:
    def __init__(self):
        # O Servidor é o "dono" do jogo.
        self.jogo = JogoGo(tamanho=9) # O Servidor cria e "guarda" a única instância do JogoGo
        self.jogadores_conectados = 0
        print("Servidor pronto. Esperando jogadores...")

    # --- Métodos que os clientes vão chamar (RMI) ---
    # Estes são os métodos que o cliente pode chamar remotamente

    def conectar(self):
        """Um novo jogador se conecta."""
        if self.jogadores_conectados >= 2:
            return 0 # Jogo cheio
            
        self.jogadores_conectados += 1
        id_jogador = self.jogadores_conectados
        print(f"Jogador {id_jogador} conectou.")
        return id_jogador # Retorna 1 para o primeiro, 2 para o segundo

    def get_estado_jogo(self):
        """Chamado pelos clientes para saber o estado do tabuleiro."""
        return self.jogo.get_estado()

    def fazer_jogada(self, id_jogador, x, y):
        """Tentativa de jogada de um cliente."""
        if id_jogador != self.jogo.jogador_atual:
            return False, "Não é a sua vez."
        
        # Chama a lógica local do jogo
        sucesso, mensagem = self.jogo.jogada_colocar_pedra(x, y)
        return sucesso, mensagem

    def passar_vez(self, id_jogador):
        """Tentativa de passar a vez de um cliente."""
        if id_jogador != self.jogo.jogador_atual:
            return False, "Não é a sua vez."
            
        mensagem = self.jogo.jogada_passar_vez()
        return True, mensagem

# --- Configuração Padrão do Pyro ---

# 1. Cria um "daemon" (serviço) para escutar na rede
daemon = Pyro5.api.Daemon()                
# 2. Procura o "cartório" (Name Server) que rodamos no Terminal 1
ns = Pyro5.api.locate_ns()                  

# --- CORREÇÃO IMPORTANTE (SINGLETON) ---
# Precisamos criar UMA SÓ instância do jogo (Singleton)
# e registrar ESSA instância.
# Todos os clientes que se conectarem falarão com este mesmo objeto.
servidor_instancia_unica = ServidorJogo()

# 3. Registra a *instância única* no daemon
uri = daemon.register(servidor_instancia_unica) 
# ------------------------------------
    
# 4. Registra esse objeto no "cartório" com um nome fácil de achar
ns.register("meu.jogo.go", uri)   # O nome "meu.jogo.go" é como o Cliente vai nos achar

print("Servidor de Go rodando. (URI: " + str(uri) + ")")
print("Pressione Ctrl+C para sair.")
# 5. Liga o servidor e o mantém escutando para sempre
daemon.requestLoop()