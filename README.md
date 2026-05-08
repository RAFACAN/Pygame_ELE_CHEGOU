# Silêncio Doméstico

`Silêncio Doméstico` é um jogo curto em `pygame` com foco em conscientização sobre violência doméstica. O jogador controla uma personagem que precisa recolher objetos da casa antes da chegada do agressor, em uma corrida contra o tempo que transforma um ambiente doméstico comum em um espaço de tensão.

O projeto foi desenvolvido como trabalho acadêmico com a proposta de usar uma mecânica simples e familiar para provocar reflexão, desconforto leve e atenção sobre um tema muitas vezes normalizado ou ignorado no cotidiano.

## Objetivo do projeto

O jogo busca:

- gerar conscientização sobre violência doméstica;
- mostrar que situações de agressão podem existir em ambientes aparentemente comuns e seguros;
- atingir principalmente jovens e adultos que não tenham contato direto com o tema;
- usar interação simples, repetição e contraste simbólico para comunicar uma mensagem social.

Em vez de apostar em sistemas complexos, o jogo trabalha com:

- coleta de objetos cotidianos;
- limite de tempo;
- escurecimento progressivo da cena;
- mudança de desfecho conforme o desempenho do jogador.

## Mecânica principal

Durante a gameplay, o jogador precisa:

1. andar pela casa;
2. coletar objetos;
3. fazer isso em até `60` segundos.

Se o objetivo não for concluído a tempo, o jogo apresenta um desfecho de impacto. Se todos os itens forem recolhidos, a cena final mostra a chegada da polícia, contenção do agressor e encerramento com mensagem de apoio e denúncia.

## Experiência que o jogo quer provocar

O projeto foi pensado para ser simples na interação e direto na mensagem.

As escolhas de design buscam provocar:

- reflexão sobre violência doméstica;
- sensação de urgência;
- leitura simbólica do ambiente doméstico;
- aprendizado indireto por meio da interação.

O contraste entre tarefas banais, cenário doméstico e ameaça iminente é o principal elemento expressivo do jogo.

## Tecnologias

- Python 3.10+
- Pygame 2.5+
- Ruff para lint

## Estrutura do projeto

```text
silencio_domestico/
  assets/
    audio/
    images/
  src/
    __main__.py
    entities.py
    game.py
    settings.py
  main.py
  pyproject.toml
  requirements.txt
  README.md
```

### Responsabilidade dos arquivos principais

- `main.py`: entrypoint simples para rodar o projeto localmente sem instalar pacote.
- `src/game.py`: loop principal, carregamento de assets, cenas, máscara de navegação e fluxo geral do jogo.
- `src/entities.py`: entidades básicas da gameplay, como personagem e itens.
- `src/settings.py`: configurações centrais de tela, sprites, tempos, seeds da máscara e nomes dos assets.

## Assets em uso

O projeto foi consolidado para usar apenas os arquivos realmente necessários em `assets/images` e `assets/audio`.

### Imagens

- `fundo_casa.png`: planta principal da casa usada na gameplay e na cena final.
- `mulher.png`: sprite da personagem jogável.
- `agressor.png`: sprite do agressor em pé.
- `agressor_abatido.png`: sprite do agressor abatido usado na cena final.
- `policial_parado.png`: sprite sheet de policial parado.
- `policial_andando.png`: sprite sheet de policial andando.
- `talheres.png`
- `batedeira.png`
- `cafeteira.png`
- `torradeira.png`
- `vassoura.png`
- `chave.png`

### Áudio

- `musica_fundo.mp3`
- `passos.wav`
- `coletar.wav`

## Navegação e colisão

O movimento da personagem usa uma máscara de navegação gerada a partir do piso da casa, com base em pontos-semente configurados em `src/settings.py`.

Isso permite que a área caminhável siga melhor a planta real do cenário do que uma solução puramente baseada em poucos retângulos grandes.

Para depuração, o jogo oferece:

- `F1`: mostra a máscara caminhável em verde e a hitbox da personagem em vermelho.

Os retângulos ainda existem como apoio para o spawn de itens, mas o deslocamento da personagem é validado pela máscara.

## Cena final

Quando o jogador conclui o objetivo:

- policiais entram em cena;
- há uma aproximação e contenção visual do agressor;
- o agressor troca para o asset `agressor_abatido.png`;
- o jogo encerra com mensagem de denúncia e apoio.

## Como executar

### Opção 1: rodar sem instalar o pacote

```powershell
python -m pip install -r requirements.txt
python main.py
```

### Opção 2: instalar o projeto localmente

```powershell
python -m pip install .
silencio-domestico
```

## Comandos úteis de desenvolvimento

### Validar sintaxe

```powershell
py -3 -m py_compile main.py src\__main__.py src\entities.py src\game.py src\settings.py
```

### Rodar lint

```powershell
.\.venv\Scripts\python -m ruff check .
```

## Controles

- `WASD` ou setas: mover a personagem
- `F1`: alternar overlay de debug da máscara de navegação
- `ESC`: sair na tela final

## Mensagem social

O jogo não trata violência doméstica como pano de fundo decorativo. A proposta é usar um sistema simples para destacar:

- como sinais podem estar inseridos em situações comuns;
- como a percepção do ambiente muda sob ameaça;
- a importância de conscientização, apoio e denúncia.

Ao final, o jogo reforça os canais de ajuda:

- `190`: emergência
- `180`: denúncia e orientação

## Integrantes do trabalho

- Rafael Cangussú Moreira — RA 32321034
- Lucas Soares Rocha — RA 324155365
- Leonardo Vieira Dias Sales — RA 323119033
- Israel Bernardo de Assis Silva — RA 325130743

## Estado atual e manutenção

O projeto foi mantido propositalmente enxuto:

- sem arquitetura pesada;
- sem camadas artificiais;
- com foco em legibilidade e execução simples em qualquer PC com Python.
