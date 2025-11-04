# GoGame.py
# Este arquivo contém apenas a lógica do jogo, sem rede.

class JogoGo:
    def __init__(self, tamanho=9):
        self.tamanho = tamanho
        self.tabuleiro = [[0 for _ in range(tamanho)] for _ in range(tamanho)]
        # 0 = Vazio
        # 1 = Jogador 1 (Preto)
        # 2 = Jogador 2 (Branco)
        self.jogador_atual = 1
        self.pedras_capturadas = {1: 0, 2: 0}
        self.passos_consecutivos = 0
        self.posicao_ko = None # variável crucial. Ela armazena uma coordenada (x, y) que se torna ilegal por exatamente uma rodada, devido à Regra de Ko.
        
    # --- Funções Auxiliares (Apoio ao Jogo) ---

    def get_estado(self):
        """Retorna um dicionário simples com o estado atual do jogo."""
        return {
            "tabuleiro": self.tabuleiro,
            "jogador_atual": self.jogador_atual,
            "capturadas_p1": self.pedras_capturadas[1],
            "capturadas_p2": self.pedras_capturadas[2],
            "fim_de_jogo": self.passos_consecutivos >= 2
        }

    # Apenas para testes locais (depuração). Não é usada na lógica principal do jogo.
    def imprimir_tabuleiro_console(self):
        """Função auxiliar para testes locais (não usada pelo cliente)."""
        print("  " + " ".join([str(i) for i in range(self.tamanho)]))
        for i, linha in enumerate(self.tabuleiro):
            print(f"{i} " + " ".join(['.' if c == 0 else 'X' if c == 1 else 'O' for c in linha]))
        print(f"Vez de: {'Preto (X)' if self.jogador_atual == 1 else 'Branco (O)'}")
        print(f"Capturadas (Preto): {self.pedras_capturadas[1]}")
        print(f"Capturadas (Branco): {self.pedras_capturadas[2]}")

    # --- As Ações do Jogador (As Jogadas) ---
    
    # --- JOGADA 1: PASSAR A VEZ ---
    def jogada_passar_vez(self):
        """O jogador atual passa a vez."""
        self.passos_consecutivos += 1
        if self.passos_consecutivos >= 2:
            print("Ambos passaram. Fim de jogo.")
            return "Fim de Jogo"
            
        self.trocar_jogador()
        return "Turno passado"

    # --- JOGADA 2: COLOCAR PEDRA ---
    def jogada_colocar_pedra(self, x, y):
        """Tenta colocar uma pedra na posição (x, y)."""
        
        # --- LÓGICA DE KO (VERIFICAÇÃO) ---
        # Armazena o Ko da jogada anterior e limpa o estado
        posicao_ko_anterior = self.posicao_ko
        self.posicao_ko = None  # O Ko só dura 1 turno, então limpamos
        
        # 1. Verifica se a jogada atual é exatamente na posição que foi marcada como Ko. Se for, a jogada é ilegal.
        if (x, y) == posicao_ko_anterior:
            # Devolve o Ko, pois o jogador não "resolveu"
            self.posicao_ko = posicao_ko_anterior 
            return False, "Jogada ilegal (Regra de Ko - não pode capturar de volta imediatamente)"
        # --- FIM DA LÓGICA DE KO ---
        
        # 2. É uma jogada válida?
        if not (0 <= x < self.tamanho and 0 <= y < self.tamanho):
            return False, "Jogada fora do tabuleiro."
        if self.tabuleiro[y][x] != 0:
            return False, "Posição já ocupada."

        # 3. Colocação otimista da pedra, se for uma jogada suicida, ela será removida depois.
        self.tabuleiro[y][x] = self.jogador_atual
        
        # 4. Lógica de Captura (A "Jogada 3")
        # Verifica se essa jogada capturou grupos *oponentes*
        oponente = 3 - self.jogador_atual
        pedras_removidas = 0
        
        # Verifica os 4 vizinhos da pedra que acabou de ser colocada
        for viz_x, viz_y in self._get_vizinhos(x, y):
            if self.tabuleiro[viz_y][viz_x] == oponente:
                # Encontramos um grupo oponente. Vamos ver se ele foi capturado.
                # Pede ao DFS: "Começando por esta pedra oponente, encontre todo o grupo dela e todas as suas liberdades."
                grupo, liberdades = self._encontrar_grupo_e_liberdades(viz_x, viz_y)
                
                if len(liberdades) == 0: # Se o grupo do oponente não tem mais liberdades, ele foi capturado!
                    # Remove o grupo do tabuleiro
                    for (px, py) in grupo:
                        self.tabuleiro[py][px] = 0
                        pedras_removidas += 1
                        
        if pedras_removidas > 0:
            self.pedras_capturadas[self.jogador_atual] += pedras_removidas
            print(f"Jogador {self.jogador_atual} capturou {pedras_removidas} pedras!")
            
        # --- INÍCIO DA LÓGICA DE SUICÍDIO ---
        # A jogada só é suicida SE:
        # 1. Não capturamos nenhuma pedra do oponente (pedras_removidas == 0)
        # 2. O grupo que acabamos de formar (ou nos juntar) não tem liberdades.

        if pedras_removidas == 0:
            # Não capturamos nada. Vamos verificar nossa própria liberdade.
            # Segunda chamda do DFS: Agora, ele verifica o grupo da sua própria pedra que acabou de ser jogada.
            grupo_atual, liberdades_atuais = self._encontrar_grupo_e_liberdades(x, y)
            
            if len(liberdades_atuais) == 0:
                # É SUICÍDIO!
                # Desfaz a jogada
                self.tabuleiro[y][x] = 0 
                
                # Restaura o Ko anterior, se houver, pois a jogada foi invalidada
                self.posicao_ko = posicao_ko_anterior
                
                # Retorna o erro
                return False, "Jogada ilegal: Suicídio não é permitido."
        # --- FIM DA LÓGICA DE SUICÍDIO ---
            
        # --- LÓGICA DE KO (DEFINIÇÃO) ---
        # Se capturamos 1 pedra E a nossa pedra que jogou
        # também só tem 1 liberdade, ativamos o Ko.
        if pedras_removidas == 1:
            # Encontra o grupo da pedra que acabamos de jogar
            grupo_recente, liberdades_recentes = self._encontrar_grupo_e_liberdades(x, y)
            
            # Se nossa pedra/grupo só tem 1 liberdade
            if len(liberdades_recentes) == 1:
                # E o grupo que jogamos só tem 1 pedra
                if len(grupo_recente) == 1:
                    # É um Ko! A posição proibida é a única liberdade
                    # (que é o buraco da pedra que acabamos de capturar).
                    self.posicao_ko = list(liberdades_recentes)[0]
                    print(f"*** REGRA DE KO ATIVADA NA POSIÇÃO: {self.posicao_ko} ***")
        # --- FIM DA LÓGICA DE KO ---

        
        self.passos_consecutivos = 0 # Reseta a contagem de "passar"
        self.trocar_jogador()
        return True, "Jogada realizada"

    def trocar_jogador(self):
        """Alterna o jogador atual entre 1 (Preto) e 2 (Branco)."""
        self.jogador_atual = 3 - self.jogador_atual


    # --- LÓGICA DE CAPTURA (A PARTE MAIS IMPORTANTE) ---
    
    def _get_vizinhos(self, x, y):
        """Retorna uma lista de coordenadas (x,y) dos vizinhos válidos."""
        vizinhos = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            vx, vy = x + dx, y + dy # Aqui, calculamos a coordenada do "vizinho candidato"
            if 0 <= vx < self.tamanho and 0 <= vy < self.tamanho: # verificação de limites
                vizinhos.append((vx, vy))
        return vizinhos

    # O "Cérebro" (O DFS)
    def _encontrar_grupo_e_liberdades(self, x, y):
        """
        Esta é a função "mágica" (algoritmo de Flood Fill / DFS).
        A partir de uma pedra em (x,y), encontra todas as pedras
        conectadas a ela e todas as liberdades (espaços vazios)
        desse grupo.
        """
        cor_do_grupo = self.tabuleiro[y][x] # Armazena a cor da pedra inicial (ex: 1 para Preto).
        if cor_do_grupo == 0:
            return set(), set() # Não é um grupo

        pedras_do_grupo = set() # Um set (conjunto) para armazenar as coordenadas (x, y) de todas as pedras que pertencem a este grupo.
        liberdades = set() # Um set para armazenar as coordenadas (x, y) de todos os espaços vazios (liberdades) adjacentes a este grupo.
        visitados = set() # Um set para rastrear as casas que já verificamos, evitando loops infinitos (ex: A visita B, B visita A).
        pilha = [(x, y)] # Pilha para o algoritmo de busca (DFS) - LIFO (Last In, First Out - O último a entrar é o primeiro a sair)

        while pilha: #Continua enquanto houver casas na pilha para explorar
            cx, cy = pilha.pop() # Pega a última casa adicionada à pilha para investigar.
            
            if (cx, cy) in visitados:
                continue # Se já visitamos esta casa, pulamos para a próxima iteração
            visitados.add((cx, cy)) # Marca a casa atual como visitada.

            # Verifica o que existe nesta casa
            cor_atual = self.tabuleiro[cy][cx]

            if cor_atual == 0:
                # É um espaço vazio, é uma liberdade!
                liberdades.add((cx, cy))
            elif cor_atual == cor_do_grupo:
                # É uma pedra do nosso grupo!
                pedras_do_grupo.add((cx, cy))
                # Adiciona seus vizinhos na pilha para serem verificados
                for (vx, vy) in self._get_vizinhos(cx, cy): # Pegamos todos os seus vizinhos.
                    if (vx, vy) not in visitados: #Para cada vizinho que ainda não visitamos...
                        pilha.append((vx, vy))
            # Se for cor do oponente, ignora (é uma "parede" do grupo)
            
        return pedras_do_grupo, liberdades # Após a pilha ficar vazia retornamos os dois conjuntos.