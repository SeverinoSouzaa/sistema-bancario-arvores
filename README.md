# Sistema Bancário — Árvores Balanceadas (AVL e Rubro-Negra)
**Trabalho Prático I — Algoritmos e Estruturas de Dados II (AED II)**  
**Docente:** Prof. Alternei Brito  

---

## 1. Identificação da Equipe

### 👥 Equipe

| # | 👤 Integrante |
| :-: | :--- |
| **01** | Severino Souza |
| **02** | Fran Robson |
| **03** | Jenner Lucas |
| **04** | Raul Berger |

---

## 2. Descrição do Projeto e Minimundo

O objetivo deste trabalho prático é projetar, implementar e comparar experimentalmente duas estruturas de dados fundamentais para busca em memória principal: a **Árvore AVL** e a **Árvore Rubro-Negra (Red-Black Tree)**, aplicando-as a uma coleção de registros idêntica.

### Minimundo Selecionado: Minimundo 6 — Sistema Bancário
A aplicação simula o gerenciamento de contas em uma instituição bancária, mantendo a coleção de registros simultaneamente em duas estruturas independentes (AVL e Rubro-Negra).

* **Entidade:** `Conta`
* **Chave de Ordenação Primária:** `numero_conta` (identificador numérico único)
* **Atributos do Registro:**
  * `numero_conta` (Chave primária): identificador único utilizado em todas as comparações de busca binária, inserção e remoção.
  * `titular` (string): nome completo do correntista.
  * `agencia` (string/int): código da agência vinculada.
  * `tipo` (string): modalidade da conta (e.g., Corrente, Poupança, Salário).
  * `saldo` (float): saldo monetário atual.

> **Regra de Ordenação (Propriedade de ABB):**  
> Para qualquer nó com chave $K$, todas as chaves da subárvore esquerda satisfazem $k_{esq} < K$ e todas as chaves da subárvore direita satisfazem $k_{dir} > K$. O atributo `saldo` e os demais dados cadastrais não afetam o posicionamento do nó na árvore.

---

## 3. Política de Chaves e Tratamento de Exceções

Em conformidade estrita com a **Seção 8 (Regras Gerais)** do enunciado:

1. **Unicidade das Chaves:** Todas as contas devem possuir números exclusivos.
2. **Política de Inserção Duplicada:** Caso haja uma tentativa de inserir uma chave já existente, o sistema **rejeita a operação**, emitindo uma notificação de aviso (`DuplicateKeyError` / mensagem em console) sem sobrescrever o nó anterior e sem desestabilizar os fatores de balanceamento ou recolorações da árvore.
3. **Tratamento Seguro de Chaves Inexistentes:** Operações de busca ou remoção por chaves que não constam na árvore são interceptadas com segurança, retornando `None` ou mensagem informativa amigável, sem provocar exceções fatais ou corrupção de ponteiros.

---

## 4. Organização do Código-Fonte

O projeto segue a modularização recomendada pela especificação, dividindo claramente as responsabilidades de modelos, estruturas de dados, interface e bateria de testes:

```text
sistema-bancario-arvores/
├── avl.py              # Implementação autoral da Árvore AVL, rotações, FB e validações
├── rubro_negra.py      # Implementação autoral da Árvore Rubro-Negra, cores, rotações e validações
├── modelos.py          # Entidade Conta e classes auxiliares de nós e métricas
├── experimentos.py     # Scripts automatizados para os Experimentos A, B, C e D
├── main.py             # Interface interativa de linha de comando (CLI com modo detalhado)
├── relatorio-final/    # Relatório Técnico PDF
│   └── Relatorio_Trabalho_Pratico_I.pdf
├── .gitignore          # Arquivos e diretórios ignorados pelo Git
└── README.md           # Documentação técnica e instruções de execução
```

> **Aviso de Integridade Acadêmica:** Conforme exigido no regulamento, ambas as árvores foram implementadas integralmente pela equipe, sem a utilização de bibliotecas prontas de terceiros para balanceamento de árvores binárias.

---

## 5. Requisitos e Ambiente de Execução

* **Linguagem:** Python 3.10 ou superior.
* **Bibliotecas Externas:** Nenhuma dependência externa obrigatória é necessária para a execução do sistema básico (utiliza apenas módulos padrão como `time`, `random`, `sys`, `dataclasses`).
* **Bibliotecas Opcionais (para experimentos e plotagem de gráficos, se configurado):**
  * `matplotlib` (geração de gráficos comparativos)
  * `tabulate` (formatação de tabelas no terminal)

### Instalação das dependências opcionais (caso queira gerar gráficos)
```bash
pip install matplotlib tabulate
```

---

## 6. Instruções de Execução

### 1. Clonando o Repositório
```bash
git clone https://github.com/SeverinoSouzaa/sistema-bancario-arvores.git
cd sistema-bancario-arvores
```

### 2. Executando o Menu Interativo
O ponto de entrada principal do sistema oferece um menu textual intuitivo que permite testar individualmente cada árvore e operação:
```bash
python main.py
```

O menu disponibiliza as seguintes opções:
1. Selecionar estrutura de trabalho (AVL ou Rubro-Negra);
2. Cadastrar nova conta (inserção com medição de rotações/recolorações);
3. Buscar conta por número (com contagem de comparações e nós visitados);
4. Remover conta por número;
5. Listar contas em ordem crescente (caminhamento em-ordem);
6. Exibir estatísticas (altura atual e quantidade de nós);
7. Exibir estatísticas de rebalanceamento (rotações simples, duplas e recolorações);
8. Validar integridade e propriedades formais da árvore;
9. Alternar Modo de Execução Detalhado (*Verbose*);
10. Executar suíte de experimentos comparativos automáticos.

### 3. Modo de Execução Detalhado (*Verbose*)
O sistema possui um modo detalhado de execução (Seção 2.4 do edital). Quando ativado via menu ou parâmetro, o console imprime passo a passo os eventos de desequilíbrio:
* Chave inserida ou removida;
* Nó onde ocorreu a violação de invariante;
* Tipo de rotação executada (Simples à Direita, Simples à Esquerda, Dupla LR ou Dupla RL);
* Recolorações efetuadas (no caso da Rubro-Negra);
* Estrutura visual da árvore no terminal após a correção.

### 4. Executando os Experimentos Comparativos
Para disparar a bateria automatizada de testes e gerar a coleta das métricas diretamente:
```bash
python experimentos.py
```

---

## 7. Validação das Propriedades das Árvores

Cada estrutura conta com um método próprio de autoauditoria e validação estrita:

### Validador AVL (`avl.validar()`)
1. **Propriedade BST:** Todo nó possui chave estritamente maior que sua subárvore esquerda e menor que sua subárvore direita.
2. **Fator de Balanceamento:** Para cada nó $u$, $|FB(u)| = |h_{dir}(u) - h_{esq}(u)| \le 1$.
3. **Consistência de Altura:** A altura declarada em cada nó reflete exatamente $1 + \max(h_{esq}, h_{dir})$.

### Validador Rubro-Negro (`rubro_negra.validar()`)
1. **Propriedade BST:** Ordem estrita das chaves em todos os nós internos.
2. **Raiz Preta:** A raiz da árvore é obrigatoriamente preta.
3. **Folhas Pretas:** Todos os nós sentinela/folhas (NIL) são pretos.
4. **Propriedade Vermelha:** Se um nó for vermelho, ambos os seus filhos são pretos (não há nós vermelhos adjacentes).
5. **Altura Negra Uniforme:** Todo caminho simples de qualquer nó até as folhas descendentes contém o mesmo número exato de nós pretos ($bh$).

---

## 8. Experimentos Comparativos e Reprodutibilidade

Para assegurar a reprodutibilidade científica (Seção 5 e 8 do enunciado), todos os testes aleatórios utilizam uma semente pseudoaleatória controlada (**`SEED = 42`**) e aplicam rigorosamente a mesma sequência de chaves e operações em ambas as estruturas.

### Síntese dos Cenários Avaliados:
* **Experimento A (Inserção Ordenada):** Inserção de chaves em ordem crescente com $n \in \{100, 1.000, 10.000\}$ para avaliar o pior caso clássico de uma BST não balanceada.
* **Experimento B (Inserção Aleatória):** Inserção de chaves uniformemente distribuídas ($n \in \{100, 1.000, 10.000\}$) com semente prefixada.
* **Experimento C (Busca com Métricas de Acesso):** Realização de buscas amostrais para chaves presentes e chaves ausentes, contabilizando o tempo total e a média de nós visitados por consulta.
* **Experimento D (Remoção Parcial):** Remoção controlada de frações dos elementos ($10\%$, $30\%$ e $50\%$), medindo tempo despendido, variação de altura, rotações e recolorações residuais.

### Tabela de Métricas Coletadas

| Métrica | Árvore AVL | Árvore Rubro-Negra |
| :--- | :---: | :---: |
| **Altura final** | Menor (mais rígida: $\approx 1.44 \log_2 n$) | Ligeiramente maior ($\le 2 \log_2(n+1)$) |
| **Rotações na inserção** | Frequentes | Raras (compensadas por recolorações) |
| **Rotações na remoção** | Podem propagar até a raiz | No máximo 3 rotações |
| **Recolorações** | Não aplicável ($0$) | Frequentes ($O(\log n)$) |
| **Média de nós visitados na busca** | Otimizada pela menor altura | Muito próxima da AVL |
| **Tempo total de inserção** | Mensurado no relatório | Mensurado no relatório |
| **Tempo total de busca** | Mensurado no relatório | Mensurado no relatório |
| **Tempo total de remoção** | Mensurado no relatório | Mensurado no relatório |

---

## 9. Checklist de Entrega

- [x] Árvore AVL implementada com rotações simples e duplas.
- [x] Árvore Rubro-Negra implementada com controle de cores, rotações e folhas NIL.
- [x] Operações de busca, inserção, remoção, mínimo, máximo e caminhamentos testadas.
- [x] Contadores independentes para rotações e recolorações implementados.
- [x] Rotinas de validação formal para os invariantes de ambas as árvores.
- [x] Tratamento robusto para chaves inexistentes e duplicadas.
- [x] Modo detalhado (*verbose*) implementado e funcional no terminal.
- [x] Bateria de experimentos comparativos automatizada e reprodutível.
- [x] Relatório técnico comparativo em PDF salvo na pasta `relatorio-final/`.
