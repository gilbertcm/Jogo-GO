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
* **RMI (Remote Method Invocation)** é focado em chamar *métodos* de *objetos* remotos (ex: `meu_jogo.fazer_jogada(x, y)`).

Para um jogo que depende de um **estado centralizado** (o tabuleiro, quem é o jogador atual, o placar), o RMI é o paradigma ideal. Ele nos permite ter um único objeto "Dono do Jogo" no servidor, e os clientes interagem com esse objeto como se ele fosse local.

**Pyro5 (Python Remote Objects)** foi escolhido por ser a implementação de RMI mais "Pythonica" e simples, permitindo expor objetos Python comuns na rede sem a necessidade de definir arquivos de interface complexos (como IDLs ou .proto).

### Componentes da Arquitetura

O sistema é composto por 3 partes que rodam de forma independente:

1.  **Servidor de Nomes (Cartório): `pyro5-ns`**
    * É um serviço padrão do Pyro5 que atua como uma "lista telefônica" ou "cartório".
    * O Servidor do Jogo se registra nele com um nome (ex: "meu.jogo.go").
    * Os Clientes o consultam para descobrir o endereço (IP e porta) do Servidor do Jogo.

2.  **Servidor do Jogo (`GoServidor.py`)**
    * É o "cérebro" e "dono" do jogo. Ele é quem possui a instância única do objeto `JogoGo`.
    * Ele se registra no Servidor de Nomes para ser encontrado.
    * Ele espera os clientes se conectarem e recebe suas chamadas de método (RMI) para `fazer_jogada()`, `passar_vez()` ou `get_estado_jogo()`.
    * **Importante:** O servidor é configurado como **Singleton**, garantindo que ambos os clientes se conectem à *mesma instância* do jogo.

3.  **Cliente (`GoCliente.py`)**
    * É a interface de terminal para o jogador.
    * Ele **não possui nenhuma lógica de jogo**. É uma interface "burra".
    * Ao iniciar, ele consulta o Servidor de Nomes para encontrar o Servidor do Jogo.
    * Em um loop, ele:
        1.  Chama `servidor_go.get_estado_jogo()` para obter o estado atual.
        2.  Desenha o tabuleiro no console.
        3.  Se for a sua vez, pede um input (`x,y` ou `passar`).
        4.  Envia o input para o servidor (ex: `servidor_go.fazer_jogada(...)`).
    * Utiliza um sistema de "polling" (sondagem) para verificar atualizações.

## 💻 Tecnologias Utilizadas

* **Python 3.13.5**
* **Pyro5:** Biblioteca para RMI (Invocação de Métodos Remotos) em Python.

## 🛠️ Pré-requisitos e Instalação

1.  Certifique-se de ter o **Python 3** instalado em sua máquina.
2.  Instale a biblioteca `Pyro5` através do pip:

    ```bash
    pip install Pyro5
    ```

## 🚀 Guia de Execução (Teste Local)

Para rodar o projeto e testar com dois jogadores na mesma máquina (como permitido pela especificação do trabalho), você precisará abrir **4 (quatro) terminais** ou prompts de comando separados, todos na pasta do projeto.

Siga esta ordem:

### Passo 1: O Servidor de Nomes (Terminal 1)

Este terminal será o "cartório".
Digite o comando:
```bash
pyro5-ns
```
Deixe este terminal aberto. Ele deve mostrar "NS running on...".

### Passo 2: O Servidor do Jogo (Terminal 2)

Este terminal rodará o cérebro do jogo.
Digite o comando:
```bash
python GoServidor.py
```
Deixe este terminal aberto. Ele deve mostrar "Servidor de Go rodando...".

### Passo 3: O Jogador 1 (Terminal 3)

Este será o primeiro cliente (Preto/X).
Digite o comando:
```bash
python GoCliente.py
```
Ele deve conectar e mostrar "Você é o Jogador 1 (Preto)".

### Passo 4: O Jogador 2 (Terminal 4)

Este será o segundo cliente (Branco/O).
Digite o comando:
```bash
python GoCliente.py
```
Ele deve conectar e mostrar "Você é o Jogador 2 (Branco)".

---

Agora você pode jogar! Alterne entre o **Terminal 3** e o **Terminal 4** para fazer suas jogadas. O tabuleiro será atualizado em ambas as telas em tempo real.

## 🗂️ Estrutura dos Arquivos

* **`GoGame.py`**
    * O "cérebro" do jogo. Contém a classe `JogoGo` com todas as regras (captura, suicídio, ko), mas não tem conhecimento sobre rede ou distribuição.
* **`GoServidor.py`**
    * O "dono" do jogo. Importa `JogoGo`, o "embrulha" na classe `ServidorJogo` e o expõe na rede usando Pyro5. Gerencia a conexão dos jogadores e repassa as chamadas de método.
* **`GoCliente.py`**
    * A interface do usuário (UI) baseada em terminal. Conecta-se ao servidor, pede o estado do jogo, desenha o tabuleiro e envia as jogadas do usuário.

## 🧑‍💻 Autor

* Gilbert Carmo Macêdo
* gilbertcm139@gmail.com
