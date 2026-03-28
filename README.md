# Fase 1 - Analisador Léxico e Gerador de Assembly para ARMv7

**Instituição:** Pontifícia Universidade Católica do Paraná - PUCPR  
**Curso:** Bacharel em Ciência da Computação  
**Professor:** Frank Coelho de Alcantara  

**Aluno:**
- João Vitor de Lima Antunes - [JoaoVAntunes](https://github.com/JoaoVAntunes)

## Descrição

Programa em Python que processa expressões aritméticas em notação polonesa reversa (RPN) a partir de arquivos de texto, utilizando um analisador léxico baseado em Autômatos Finitos Determinísticos (AFD) com estados implementados por funções. A partir do vetor de tokens, gera código Assembly compatível com ARMv7 DEC1-SOC (v16.1) para execução no CPUlator.

## 1. Como compilar

O projeto é escrito em Python puro e não requer compilação. Basta ter o Python 3 instalado.

**Requisitos:**
- Python 3.10 ou superior

Não há dependências externas para execução do programa principal.

## 2. Como executar

O programa recebe o(s) arquivo(s) de teste como argumento(s) na linha de comando:

```bash
python main.py <arquivo1.txt> [arquivo2.txt] [arquivo3.txt] ...
```

Exemplos:

```bash
python main.py input1.txt
python main.py input1.txt input2.txt input3.txt
```

O programa irá:
1. Ler cada arquivo e processar linha a linha
2. Executar a análise léxica (AFD) de cada expressão
3. Avaliar o resultado de cada expressão
4. Gerar o código Assembly ARMv7 consolidado em `output.txt`

## 3. Como testar

### Arquivos de teste válidos

| Arquivo | Linhas | Descrição |
|---|---|---|
| `input1.txt` | 12 | Todas as operações com reais (3.5, 2.5, etc.), MEM como MEMA |
| `input2.txt` | 12 | Todas as operações, MEM como VARA, RES com N=1 |
| `input3.txt` | 12 | Todas as operações, MEM como VARB, RES com N=2 |
| `input4.txt` | 12 | Todas as operações com inteiros, MEM como VARC, aninhamento com ^ |

Cada arquivo cobre todas as operações exigidas:
- Adição (`+`), Subtração (`-`), Multiplicação (`*`), Divisão real (`/`)
- Divisão inteira (`//`), Resto (`%`), Potenciação (`^`)
- Comando especial `(N RES)` — retorna resultado de N linhas anteriores
- Comando especial `(V MEM)` — armazena valor em memória
- Comando especial `(MEM)` — lê valor da memória
- Expressões aninhadas sem limite

### Arquivo de entradas inválidas

O arquivo `invalid_Inputs.txt` contém casos de erro para validar o analisador léxico:

| Entrada | Erro detectado |
|---|---|
| `(3.14 2.0 &)` | Caractere inválido `&` |
| `(3.14.5 2 +)` | Número malformado (dois pontos) |
| `(3,45 2 +)` | Vírgula como separador decimal |
| `(10 res)` | Keyword `res` em minúscula (inválida) |
| `(abc)` | Letras minúsculas (token inválido) |
| `(5 MEMa)` | Variável com minúscula misturada |
| `(3.0 2.0 +))` | Parênteses desbalanceados (excesso) |
| `((3.0 2.0 +)` | Parênteses desbalanceados (faltando) |

### Executando os testes

```bash
python main.py input1.txt input2.txt input3.txt input4.txt
```

O código Assembly gerado será salvo em `output.txt` e pode ser executado no [CPUlator ARMv7 DE1-SoC](https://cpulator.01xz.net/?sys=arm-de1soc).

## Estrutura do Projeto

```
main.py                 # Programa principal
output.txt              # Código Assembly gerado (última execução)
input1.txt              # Arquivo de teste 1
input2.txt              # Arquivo de teste 2
input3.txt              # Arquivo de teste 3
input4.txt              # Arquivo de teste 4
invalid_Inputs.txt      # Entradas inválidas para teste do AFD
auxiliar/
    __init__.py
    afd.py              # Autômato Finito Determinístico (estados como funções)
    Exception.py        # Classe ErroLexico
    rpn.py              # Avaliador de expressões RPN
    validarParenteses.py # Validação de balanceamento de parênteses
    gerador_assembly.py  # Gerador de código Assembly ARMv7
```

## Operações Suportadas

| Operação | Sintaxe | Exemplo | Resultado |
|---|---|---|---|
| Adição | `(A B +)` | `(3.5 2.5 +)` | 6.0 |
| Subtração | `(A B -)` | `(10.0 4.0 -)` | 6.0 |
| Multiplicação | `(A B *)` | `(6.0 7.0 *)` | 42.0 |
| Divisão real | `(A B /)` | `(22.0 7.0 /)` | 3.14... |
| Divisão inteira | `(A B //)` | `(20 3 //)` | 6.0 |
| Resto | `(A B %)` | `(20 3 %)` | 2.0 |
| Potenciação | `(A B ^)` | `(2.0 3 ^)` | 8.0 |
| Resultado anterior | `(N RES)` | `(5 RES)` | 5º resultado anterior |
| Armazenar em memória | `(V MEM)` | `(10.5 MEMA)` | Salva 10.5 em MEMA |
| Ler memória | `(MEM)` | `(MEMA)` | Valor de MEMA |
| Aninhamento | `((A B op) (C D op) op)` | `((3 2 +) (4 5 *) *)` | 100.0 |
