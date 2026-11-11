
# ⚡ NTO Idle — Overdrive Ultimate Bot (100 Modules Edition)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?logo=playwright&logoColor=white)
![Architecture](<https://img.shields.io/badge/Architecture-100%20Modules-00d2ff>)
![UI](<https://img.shields.io/badge/HUD-Shadow%20DOM-162447>)
![Tests](<https://img.shields.io/badge/Tests-Unittest%20Passing-10b981>)

Sistema avançado de automação, telemetria em tempo real, inteligência adaptativa e simulação matemática desenvolvido para o MMORPG **NTO Idle** (`https://ntoidle.online/game`).

O projeto opera através do **Playwright (Chromium)** utilizando eventos físicos via protocolo **CDP (`isTrusted: true`)**, um motor de **Inteligência Artificial (Multi-Armed Bandit)** e uma interface escura completa renderizada em **Shadow DOM** diretamente sobre a tela do jogo.

---

## 📋 Índice

1. [Visão Geral e Arquitetura](#-visão-geral-e-arquitetura)
2. [Sistemas do Jogo Integrados](#-sistemas-do-jogo-integrados)
3. [Painel de Controle (5 Abas na Tela)](#-painel-de-controle-5-abas-na-tela)
4. [Catálogo Completo dos 100 Módulos (M001 a M100)](#-catálogo-completo-dos-100-módulos-m001-a-m100)
5. [Fórmulas Matemáticas e Motor Econômico](#-fórmulas-matemáticas-e-motor-econômico)
6. [Instalação e Execução](#-instalação-e-execução)
7. [Estrutura de Arquivos e Segurança](#-estrutura-de-arquivos-e-segurança)

---

## 🏗️ Visão Geral e Arquitetura

Diferente de macros simples ou scripts de console que travam a página ou usam cliques sintéticos facilmente detectáveis, o **NTO Overdrive Ultimate** é construído sobre 5 pilares de engenharia:

1. **Interação Física via CDP (`isTrusted: true`):** Todos os cliques no mapa, botões de interface e disparos de teclas (`1` a `0`, `F1`) são enviados pelo protocolo de hardware virtual do navegador com micro-variação espacial ($\pm 3\text{ px}$) e temporal ($\pm 18\%$).
2. **Interface Isolada em Shadow DOM:** O painel flutuante é encapsulado dentro de uma árvore Shadow DOM própria com proteção de sobreposição (`z-index: 2147483647`), permitindo arrastar, minimizar e controlar tudo dentro da própria janela do jogo.
3. **Orquestrador de 100 Módulos (`RegistroCemModulos`):** Cada subsistema possui um identificador único (`M001` a `M100`), contador individual de execuções em tempo real, chave liga/desliga independente e salvamento automático em JSON com backup (`.backup.json`).
4. **IA Adaptativa (Multi-Armed Bandit):** O bot avalia a cada 25 segundos qual cadência de combate gera a maior taxa de experiência e drops por minuto na hunt atual e ajusta a velocidade sozinho.
5. **Auto-Teste na Inicialização (`unittest`):** Antes de abrir o navegador, o script executa uma bateria de testes unitários para validar os 100 módulos, o conversor de moedas, o laboratório experimental e o extrator de telemetria.

---

## 🎮 Sistemas do Jogo Integrados

O bot lê e interage automaticamente com os elementos reais da interface do **NTO Idle**:

* **Painel `PROGRESSÃO`:** Leitura contínua de `LEVEL`, `XP restante para upar`, `STAMINA`, `MAGIC LEVEL`, `Chakra restante para upar`, `VH. ATAQUE`, `ESPADA`, `LUVA` e `ESCUDO`, além de clique automático no botão `+` de evolução.
* **Painel `BOT` Nativo (`COMBATE` & `AUTO HUNT`):** Monitoramento e reativação automática das chaves `AUTO TARGET`, `AUTO ATTACK` (incluindo alternância entre os presets `1` e `2` e sincronização com os tempos de recarga `40`, `60`, `105`, `20` e `145`), `AUTO HASTE` (`BigSpeed Up`), `AUTO HEAL`, `AUTO BUFF` (`Susanoo`) e `CHAKRA DOWN` (`Chakra 30%`).
* **Barra `HABILIDADES`:** Disparo priorizado por tempo de recarga nos 10 slots de jutsus (`1` a `0`).
* **Widget `MISSÕES`:** Identificação do monstro da missão ativa (ex.: `Bezer`), leitura do contador de abates (`0 / 50`) e clique automático para entrega e renovação ao atingir `100%`.
* **Dock Superior (`EXPLORAR`):** Botões de navegação rápida integrados ao painel para abrir `MERCADO`, `INVENTÁRIO`, `JUTSUS`, `TRAJES`, `FORJA`, `PROGRESSÃO`, `MAPA`, `MINI BOSSES` e `RANKING`.
* **Console `SERVER LOG` & `DEATH CHANNEL`:** Captura automática de todos os itens coletados (`Sistema: ! Pegou Nx item.`), leitura da tabela de preços em `Gold`, `Dollar` e `Cent` e detecção instantânea de alertas de morte/PK.

---

## 🖥️ Painel de Controle (5 Abas na Tela)

O painel possui botões globais no topo (**`ATIVAR BOT (ON/OFF)`**, **`🔥 OVERDRIVE 100%`**, **`🛑 PANIC`** e **`_` Minimizar**) e é dividido em 5 abas:

1. **`📊 Dashboard`:** Exibe 4 cartões de telemetria em tempo real (`Level/ML/Stamina`, `XP/h e ETA`, `DPS e Status de Vida Infinita`, `Hunt/Missão e Lucro Acumulado`), controle deslizante de velocidade (`150ms` a `1000ms`), recomendações da IA, atalhos do menu `EXPLORAR` e console de logs ao vivo.
2. **`⚔️ Combate & Hunts`:** Mostra o contador de ciclos de combate, trocas de preset (`1` ↔ `2`) e a memória histórica de rendimento (`XP/h` e `drops/h`) de cada monstro caçado.
3. **`🎒 Inv & Feira Ninja`:** Apresenta o patrimônio total acumulado na sessão convertido em `Gold`, `Dollar` e `Cent`, a contagem de drops separados por raridade (`Common`, `Uncommon`, `Rare`, `Epic`, `Legendary`) e o catálogo de preços lido do `SERVER LOG`.
4. **`🧪 Laboratório`:** Sandbox matemático onde você define o HP e o DPS do inimigo/boss e simula instantaneamente o seu Multiplicador de Ataque, DPS Padrão vs. Overdrive, Pico de Burst de 10 Jutsus, viabilidade de Instakill em 1 ciclo e condição de Vida Infinita ($HPS \ge DPS$).
5. **`🧩 100 Módulos`:** Lista interativa com barra de pesquisa em tempo real para filtrar, ativar ou desativar individualmente qualquer um dos 100 módulos (`M001` a `M100`), exibindo a categoria e o número de execuções de cada módulo.

---

## 🧩 Catálogo Completo dos 100 Módulos (`M001` a `M100`)

### 1. Inteligência e Análise (`M001` – `M010`)

| Código        | Nome do Módulo            | Função Real no Sistema                                              |
| :------------- | :------------------------- | :-------------------------------------------------------------------- |
| **M001** | Analisador do Jogo         | Varredura estrutural do DOM e estado geral da janela do jogo.         |
| **M002** | Leitor de Atributos        | Extração via Regex de Level, ML, VH. Ataque, Espada, Luva e Escudo. |
| **M003** | Monitor de Personagem      | Acompanhamento de Stamina, XP restante e Chakra restante.             |
| **M004** | Analisador de Monstros     | Identificação da criatura ativa na hunt e nas missões.             |
| **M005** | Analisador de Bosses       | Monitoramento de parâmetros para confronto com Mini Bosses.          |
| **M006** | Identificador de Hunts     | Mapeamento da área de caça atual e pareamento com histórico.       |
| **M007** | Analisador de Jutsus       | Ponderação dos tempos de recarga dos 5 slots (`20s` a `145s`).  |
| **M008** | Analisador de Equipamentos | Identificação de peças de equipamento coletadas no log.            |
| **M009** | Analisador de Recompensas  | Contabilização de ganhos de missão e drops por ciclo.              |
| **M010** | Detector de Erros          | Captura de exceções de rede, timeouts de DOM e falhas de clique.    |

### 2. Farm e Evolução (`M011` – `M020`)

| Código        | Nome do Módulo                 | Função Real no Sistema                                                 |
| :------------- | :------------------------------ | :----------------------------------------------------------------------- |
| **M011** | Farm Automático                | Manutenção contínua de `AUTO TARGET` e `AUTO ATTACK` em `ON`.   |
| **M012** | Farm Inteligente                | Sincronização entre abate, coleta em espiral e renovação de missão. |
| **M013** | Seleção Automática de Hunt   | Avaliação da hunt mais rentável registrada na memória da IA.         |
| **M014** | Otimizador de Experiência      | Minimização de tempo ocioso entre abates para maximizar XP.            |
| **M015** | Calculadora de XP por Hora      | Cálculo exato de XP/h baseado na redução de `Falta X XP para upar`. |
| **M016** | Monitor de Evolução           | Cálculo de ETA (tempo estimado em minutos) para o próximo nível.      |
| **M017** | Gerenciador de Níveis          | Atualização automática de multiplicadores ao subir de Level/ML.       |
| **M018** | Gerenciador de Transformações | Garantia de manutenção de transformações/buffs (`Susanoo`).        |
| **M019** | Otimizador de Progressão       | Clique automático nos botões `+` de atributos disponíveis.          |
| **M020** | Planejador de Evolução        | Projeção de ganho de poder por ponto investido em atributos.           |

### 3. Combate (`M021` – `M030`)

| Código        | Nome do Módulo                      | Função Real no Sistema                                                          |
| :------------- | :----------------------------------- | :-------------------------------------------------------------------------------- |
| **M021** | Gerenciador de Ataques               | Disparo coordenado de atalhos de combate via hardware virtual CDP.                |
| **M022** | Seleção Automática de Jutsus      | Priorização dos slots de menor cooldown na barra `HABILIDADES`.               |
| **M023** | Rotação Inteligente de Habilidades | Execução da fila ponderada (`4, 1, 2, 4, 1, 3, 5...`) sem travamentos.        |
| **M024** | Otimizador de Dano                   | Eliminação de intervalos mortos entre magias de diferentes presets.             |
| **M025** | Calculadora de DPS                   | Cálculo em tempo real do dano por segundo padrão vs. Overdrive.                 |
| **M026** | Analisador de Resistência           | Cálculo do percentual de mitigação de dano (`Escudo` + `Susanoo`).         |
| **M027** | Simulador de Dano Máximo            | Estimativa de dano acumulado na janela de Burst de 10 jutsus.                     |
| **M028** | Gerenciador de Cooldown              | Controle de frequência de envio de teclas conforme recarga real.                 |
| **M029** | Analisador de Combos                 | Alternância sem colisão (Mutex) entre as abas `1` e `2` do `AUTO ATTACK`. |
| **M030** | Simulador de Instakill Autorizado    | Cálculo matemático de viabilidade de abate em 1 ciclo no Laboratório.          |

### 4. Hunts e Bosses (`M031` – `M040`)

| Código        | Nome do Módulo                  | Função Real no Sistema                                              |
| :------------- | :------------------------------- | :-------------------------------------------------------------------- |
| **M031** | Detector de Monstros             | Leitura dinâmica do alvo ativo no widget de missões e combate.      |
| **M032** | Priorização de Alvos           | Foco automático no alvo travado pelo `AUTO TARGET`.                |
| **M033** | Gerenciador de Hunts             | Entrega e renovação automática de missões ao atingir `50 / 50`. |
| **M034** | Otimizador de Rotas              | Redução de cliques redundantes durante a movimentação de caça.   |
| **M035** | Monitor de Respawn               | Acompanhamento da taxa de abates por minuto na área atual.           |
| **M036** | Rastreador de Bosses             | Atalho e monitoramento de status para a janela `MINI BOSSES`.       |
| **M037** | Gerenciador de Bosses            | Ajuste de perfil de Burst máximo para abates de alta vida.           |
| **M038** | Calculadora de Dificuldade       | Comparação entre o DPS do boss e o HPS de cura do personagem.       |
| **M039** | Analisador Recompensas de Bosses | Registro de drops especiais obtidos após abates de chefes.           |
| **M040** | Histórico de Caçadas           | Armazenamento de estatísticas de XP/h e Loots/h por criatura.        |

### 5. Sobrevivência (`M041` – `M050`)

| Código        | Nome do Módulo              | Função Real no Sistema                                               |
| :------------- | :--------------------------- | :--------------------------------------------------------------------- |
| **M041** | Monitor de HP                | Vigilância contínua dos sistemas de cura e estado de vida.           |
| **M042** | Monitor de Recursos          | Monitoramento de Chakra (`Chakra 30%`) e tempo de Stamina.           |
| **M043** | Recuperação Automática    | Disparo de tecla de suporte (`F1`) e auditoria do `AUTO HEAL`.     |
| **M044** | Gerenciador de Defesa        | Manutenção forçada de `AUTO BUFF` (`Susanoo`) e `AUTO HASTE`. |
| **M045** | Detector de Perigo           | Leitura de mensagens críticas de dano e queda de conexão.            |
| **M046** | Sistema de Emergência       | Acionamento automático do modo `PANIC` e alarme sonoro (`Beep`).  |
| **M047** | Simulador de Vida Infinita   | Verificação matemática de estabilidade ($HPS \ge DPS_{inimigo}$). |
| **M048** | Analisador de Morte          | Inspeção de alertas de morte no `SERVER LOG` e `DEATH CHANNEL`.  |
| **M049** | Otimizador de Sobrevivência | Reativação imediata de chaves defensivas desarmadas após lag.       |
| **M050** | Gerenciador de Consumíveis  | Suporte ao acionamento periódico de hotkeys de poções/pergaminhos.  |

### 6. Inventário e Equipamentos (`M051` – `M060`)

| Código        | Nome do Módulo                 | Função Real no Sistema                                                       |
| :------------- | :------------------------------ | :----------------------------------------------------------------------------- |
| **M051** | Leitor de Inventário           | Captura em tempo real de todas as linhas `Sistema: ! Pegou...`.              |
| **M052** | Organizador de Itens            | Coleta automática em espiral nos 9 SQMs ao redor do personagem.               |
| **M053** | Identificador de Equipamentos   | Reconhecimento de itens como `chunnin armor`, `anbu mask`, `gaara legs`. |
| **M054** | Comparador de Atributos         | Avaliação de ganho de poder de equipamentos por raridade.                    |
| **M055** | Otimizador de Equipamentos      | Sugestão de melhoria de set com base nos itens coletados.                     |
| **M056** | Gerenciador de Itens Raros      | Contabilização separada de drops `Rare`, `Epic` e `Legendary`.         |
| **M057** | Detector de Itens Valiosos      | Destaque no log para equipamentos de alto valor em `Gold`/`Dollar`.        |
| **M058** | Histórico de Equipamentos      | Lista cronológica de todos os drops obtidos na sessão.                       |
| **M059** | Gerenciador de Recursos         | Controle da cadência de cliques de coleta para não travar o combate.         |
| **M060** | Planejador de Melhorias (Forja) | Acesso rápido e contagem de cópias de itens para uso na `FORJA`.           |

### 7. Economia (`M061` – `M070`)

| Código        | Nome do Módulo            | Função Real no Sistema                                                   |
| :------------- | :------------------------- | :------------------------------------------------------------------------- |
| **M061** | Analisador da Feira Ninja  | Extração automática de preços anunciados no `SERVER LOG`.            |
| **M062** | Monitor de Preços         | Atualização dinâmica do valor unitário de cada item em `Cent`.       |
| **M063** | Comparador de Ofertas      | Comparação entre o valor base de catálogo e ofertas do chat.            |
| **M064** | Calculadora de Lucro       | Conversão e soma do patrimônio total em `Gold`, `Dollar` e `Cent`. |
| **M065** | Histórico de Transações | Registro de cada item coletado com horário e valor estimado.              |
| **M066** | Gerenciador de Vendas      | Estimativa de receita líquida ao vender o lote de drops acumulados.       |
| **M067** | Gerenciador de Compras     | Identificação de itens abaixo do preço médio para aquisição.         |
| **M068** | Avaliador de Itens         | Precificação automática de novos drops com base na tabela de mercado.   |
| **M069** | Analisador de Mercado      | Atalho direto para o módulo `MERCADO` e aba `NEGOCIAR`.               |
| **M070** | Planejador Econômico      | Projeção de ganho de `Gold/h` e `Dollar/h` na hunt atual.            |

### 8. Inteligência Artificial (`M071` – `M080`)

| Código        | Nome do Módulo                       | Função Real no Sistema                                               |
| :------------- | :------------------------------------ | :--------------------------------------------------------------------- |
| **M071** | Aprendizado por Resultados            | Algoritmo Bandit que pontua estratégias por XP e drops obtidos.       |
| **M072** | Memória de Hunts                     | Dicionário persistente de eficiência média por criatura.            |
| **M073** | Aprendizado de Estratégias           | Teste automático entre 4 perfis de delay (`200ms` a `450ms`).     |
| **M074** | Previsão de Desempenho               | Estimativa de abates por minuto e tempo para conclusão de missão.    |
| **M075** | Identificação de Padrões           | Detecção de queda de rendimento por área vazia ou stamina baixa.    |
| **M076** | Seleção Inteligente de Estratégias | Balanceamento 80% Exploitação (melhor ritmo) / 20% Exploração.     |
| **M077** | Análise de Eficiência               | Cálculo da relação entre cliques disparados e recompensas reais.    |
| **M078** | Otimização Automática              | Ajuste autônomo de cadência sem necessidade de intervenção manual. |
| **M079** | Comparação de Resultados            | Confronto entre o rendimento da hunt atual e hunts anteriores.         |
| **M080** | Sistema de Recomendações            | Geração de dicas táticas em tempo real no painel principal.         |

### 9. Interface e Controle (`M081` – `M090`)

| Código        | Nome do Módulo             | Função Real no Sistema                                                   |
| :------------- | :-------------------------- | :------------------------------------------------------------------------- |
| **M081** | Dashboard Principal         | Visão consolidada de KPIs e barra de atalhos do menu `EXPLORAR`.        |
| **M082** | Painel de Combate           | Monitoramento de rotações de jutsus e trocas de abas `1` e `2`.      |
| **M083** | Painel de Farm              | Acompanhamento de missões ativas e memória de caçadas.                  |
| **M084** | Painel de Evolução        | Exibição de atributos reais, XP restante e ETA de nível.                |
| **M085** | Painel de Equipamentos      | Resumo de drops coletados classificados por raridade.                      |
| **M086** | Painel Econômico           | Exibição do saldo acumulado em `Gold/Dollar/Cent` e tabela de preços. |
| **M087** | Painel de Estatísticas     | Métricas de DPS, mitigação e índice de sustentação.                  |
| **M088** | Gerenciador de Módulos     | Interface com busca e checkboxes para os 100 módulos.                     |
| **M089** | Sistema de Configurações  | Controle deslizante de velocidade e botões de ativação rápida.         |
| **M090** | Monitoramento em Tempo Real | Sincronização assíncrona entre Python e Shadow DOM a cada ciclo.        |

### 10. Engenharia e Segurança (`M091` – `M100`)

| Código        | Nome do Módulo                    | Função Real no Sistema                                                      |
| :------------- | :--------------------------------- | :---------------------------------------------------------------------------- |
| **M091** | Sistema de Logs                    | Console rolável com horário e filtro de até 80 eventos recentes.           |
| **M092** | Monitor de Erros                   | Tratamento silencioso de exceções para evitar queda do loop.                |
| **M093** | Detector Falhas de Sincronização | Verificação e correção de botões nativos que desarmam por lag.           |
| **M094** | Gerenciador de Sessões            | Contexto persistente do Chromium salvando login em pasta local.               |
| **M095** | Backup de Configurações          | Cópia automática para `nto_overdrive_100.backup.json` ao iniciar.         |
| **M096** | Recuperação de Falhas            | Reinjeção automática da interface caso a página sofra reload (`F5`).    |
| **M097** | Testes Automatizados               | Suíte `unittest` validando os 100 módulos antes da execução.            |
| **M098** | Auditoria de Segurança Autorizada | Garantia de operação 100% client-side sem pacotes adulterados.              |
| **M099** | Otimizador de Desempenho           | Uso de `domcontentloaded` e sleeps curtos (`20ms`) para baixo uso de CPU. |
| **M100** | Sistema de Atualização Modular   | Persistência imediata em JSON ao alterar qualquer chave na UI.               |

---

## 🧮 Fórmulas Matemáticas e Motor Econômico

### 1. Conversão Monetária (`MotorEconomia`)

O jogo utiliza três moedas (`Gold`, `Dollar` e `Cent`). O bot converte todas as cotações lidas do `SERVER LOG` para a base unificada em **Cent**:

$$
\text{Valor Total (Cent)} = (\text{Gold} \times 10.000) + (\text{Dollar} \times 100) + \text{Cent}
$$

### 2. Cálculo de DPS e Sustentação (`LaboratorioExperimental`)

* **Multiplicador de Atributos:**
  $$
  M_{\text{atk}} = 1 + (0,012 \times \text{Level}) + (0,035 \times \text{ML}) + (0,020 \times \text{Espada})
  $$
* **Mitigação de Defesa (`Susanoo` + `Escudo`):**
  $$
  \text{Mitigação} = \min(0,75,\; 0,25 + 0,018 \times \text{Escudo})
  $$
* **Índice de Vida Infinita (Estabilidade de Sustain):**
  $$
  I_{\text{sustain}} = \frac{\text{HPS}_{\text{cura}}}{\text{DPS}_{\text{inimigo}} \times (1 - \text{Mitigação})}
  $$

  Se $I_{\text{sustain}} \ge 1,0$, a regeneração supera o dano líquido recebido (**Status: IMORTAL**).

---

## 🛠️ Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone [https://github.com/teylonkkjk/nto-overdrive-bot.git](https://github.com/teylonkkjk/nto-overdrive-bot.git)
cd nto-overdrive-bot
```

### 2. Instalar as Dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Executar os Testes Automatizados (Opcional)

Para validar os 100 módulos e as fórmulas no terminal sem abrir o navegador:

```bash
python runner.py --test
```

### 4. Iniciar o Bot Completo

```bash
python runner.py
```

---

## 📂 Estrutura de Arquivos e Segurança

```text
nto-overdrive-bot/
├── runner.py                      # Código-fonte completo (Motor, IA, Laboratório, Testes e UI)
├── requirements.txt               # Dependências do Python (Playwright)
├── nto_overdrive_100.json         # Configuração persistente dos 100 módulos (gerado automaticamente)
├── nto_overdrive_100.backup.json  # Backup automático de segurança (ignorado pelo Git)
├── sessao_nto_overdrive/          # Cookies e sessão de login local (ignorado pelo Git)
├── .gitignore                     # Regras de proteção para não enviar cookies ao GitHub
└── README.md                      # Documentação completa do projeto
```

> **⚠️ Aviso de Segurança:** A pasta `sessao_nto_overdrive/` armazena os cookies de autenticação da sua conta localmente para que você não precise fazer login toda vez. O arquivo `.gitignore` já está configurado para **nunca** enviar essa pasta ao GitHub.
