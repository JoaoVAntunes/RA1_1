#João Vitor de Lima Antunes - JoaoVAntunes
#RA1 1

import sys
from afd import *

def lerArquivo(nomeArquivo):
    try:
        with open(nomeArquivo, "r") as arq:
            return arq
    
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nomeArquivo}' não encontrado.")
    except IOError as e:
        print(f"Erro ao ler arquivo: {e}")


def mostrar_erros(linha, erros):
    for msg, pos in erros:
        print(linha)
        print(" " * pos + "^", msg)

def parseExpressao(linha):
    """
    Converte uma linha em tokens usando AFD.
    Retorna: lista de tuplas (TIPO, VALOR)
    """
    tokens, erros = [], []
    estado = estado_inicial
    i = 0
    lexema = ""

    while i < len(linha):
        estado, i, lexema, tokens = estado(linha, i, lexema, tokens)
        if tokens and tokens[-1][0] == "ERRO":
            msg = tokens[-1][1]
            pos = tokens[-1][2]  # existe porque ERRO sempre tem 3 campos
            erros.append((msg, pos))

    if erros:
        mostrar_erros(linha, erros)

    return tokens


'''def balanceamentoParenteses(linha):
    openParentheses = 0
    closedParentheses = 0

    #para cada caracter
        if x == "(":
            openParentheses += 1
    
        if x == ")":
            closedParentheses += 1

    result = openParentheses - closedParentheses

    if result != 0:
        return False

    return True

def executarExpressao(expressao):
    return ""

def gerarAssembly(expressao):
    return ""

def exibirResultados(expressao):
    print("Resultados para a expressão:", expressao)
    print("Expressão parseada:", parseExpressao(expressao))
    print("Resultado da execução:", executarExpressao(expressao))
    print("Código Assembly gerado:", gerarAssembly(expressao))


nome_arquivo = sys.argv[1]
text_file = lerArquivo(nome_arquivo)

parseExpressao(text_file, )'''
print(parseExpressao("(3.14 2.0 +)"))
print(parseExpressao("(5 RES)"))
print(parseExpressao("(10.5 CONTADOR)"))
print(parseExpressao("(10.5 & 2.)"))
print(parseExpressao("(3,)"))