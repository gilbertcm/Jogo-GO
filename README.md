# Jogo de Go (9x9) Distribuído com Python e Pyro5

> **Nota:** Este é um projeto acadêmico desenvolvido para a disciplina de Sistemas Distribuídos, com o objetivo de aplicar conceitos de comunicação remota (RMI/RPC) na prática.

Este projeto implementa uma versão básica, porém funcional, do jogo de tabuleiro Go em um grid 9x9. A aplicação é totalmente distribuída, permitindo que dois jogadores, em máquinas ou processos diferentes, joguem um contra o outro em tempo real através da rede.

## 🎮 Funcionalidades Principais

O jogo implementa as regras fundamentais do Go para garantir uma partida funcional. O requisito mínimo era de 3 lógicas de jogo, e o projeto final implementa **2 ações de jogador** e **3 regras de sistema complexas**:

### Ações do Jogador
1.  **Colocar Pedra:** O jogador escolhe uma coordenada `(x,y)` para posicionar sua pedra.
2.  **Passar a Vez:** O jogador opta por não jogar, passando o turno ao oponente. (Se ambos os jogadores passarem consecutivamente, o jogo termina).

### Regras de Sistema (Lógicas de Validação)
1.  **Lógica de Captura:** O sistema detecta automaticamente se uma jogada removeu a última "liberdade" (espaço vazio adjacente) de um grupo oponente. Se sim, o grupo é capturado, removido do tabuleiro e contabilizado no placar.
2.  **Regra de Suicídio:** O sistema proíbe um jogador de colocar uma pedra em uma posição onde ela (ou o grupo ao qual ela se junta) ficaria sem nenhuma liberdade, *a menos que* essa mesma jogada resulte na captura de um grupo oponente.
3.  **Regra de Ko (Eternidade):** O sistema impede loops infinitos. Se um jogador captura uma única pedra, o oponente é proibido de, na jogada *imediatamente* seguinte, recapturar a pedra se isso retornar o tabuleiro ao estado exato anterior.

## 🏛️ Arquitetura Distribuída

A aplicação segue uma arquitetura **Cliente-Servidor** clássica, utilizando **RMI (Remote Method Invocation)** como paradigma de comunicação.

### Por que Pyro5 (RMI) e não RPC?

* **RPC (Remote Procedure Call)** é focado em chamar *funções* remotas (ex: `calcular_soma(a, b)`).
* **RMI (Remote Method Invocation)** é focado em chamar *métodos
