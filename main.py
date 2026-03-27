#João Vitor de Lima Antunes - JoaoVAntunes
#RA1 1

import sys
import json
from afd import *
from Exception import ErroLexico


def lerArquivo(nomeArquivo):
    """Lê arquivo e retorna lista de linhas"""
    try:
        with open(nomeArquivo, "r", encoding="utf-8") as arq:
            return [linha.strip() for linha in arq.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nomeArquivo}' não encontrado.")
        return []
    except IOError as e:
        print(f"Erro ao ler arquivo: {e}")
        return []


def validarBalanceamentoParenteses(tokens):
    """Valida balanceamento de parênteses (parte do AFD)"""
    contador = 0
    for token in tokens:

        if len(token) != 2:
            continue
        
        tipo, _ = token
        if tipo == "L_PARENTESES":
            contador += 1
        elif tipo == "R_PARENTESES":
            contador -= 1
        
        if contador < 0:
            raise ErroLexico("Parêntese de fechamento sem abertura", "Unknown position")
    
    if contador > 0:
        raise ErroLexico("Parêntese aberto sem fechamento", "Unknown position")


def parseExpressao(linha):
    """
    Converte uma linha em tokens usando AFD.
    Lança ErroLexico se encontrar erro léxico ou desbalanceamento.
    """
    vetor_tokens = []
    estado = estado_inicial
    i = 0
    lexema = ""
    
    print("[INÍCIO] Expressão:", repr(linha), "len=", len(linha),"\n\n")

    try:
        iteracao = 0
        while i < len(linha):
            iteracao += 1
            char_atual = linha[i]
            print(f"  [LOOP {iteracao}] i={i}, char={repr(char_atual)}, estado={estado.__name__}, lexema={repr(lexema)}")
            estado, i, lexema, vetor_tokens = estado(linha, i, lexema, vetor_tokens)
            print(f"           -> após: i={i}, tokens_count={len(vetor_tokens)}")
        
        print(f"\n[SAIU DO LOOP] i={i}, len={len(linha)}, estado={estado.__name__}, lexema={repr(lexema)}")
        print(f"[TOKENS ANTES VALIDAÇÃO] {vetor_tokens}")


        validarBalanceamentoParenteses(vetor_tokens)
    
        print("[FIM] Expressão processada com sucesso")

    except ErroLexico as e:
        # Re-lançar para ser tratado pelo chamador
        raise
    

    return vetor_tokens


def executarExpressao(expressao):

    return ""


def gerarAssembly(expressao):

    return ""


def exibirResultados(expressao):

    print("Resultados para a expressão:", expressao)


if __name__ == "__main__":
    todos_tokens = []

    if len(sys.argv) > 1:
        # lê arquivo(s), mas processa linha a linha
        for nomeArquivo in sys.argv[1:]:
            linhas = lerArquivo(nomeArquivo)
            if not linhas:
                continue
            for linha in linhas:
                try:
                    tokens = parseExpressao(linha)     # string única
                    todos_tokens.append(tokens)
                    print(f"\n\nOK: {linha} -> {tokens}")
                except ErroLexico as e:
                    print(f"\n\nERRO: {linha} -> {e.mensagem} (pos {e.posicao})")
    else:
        print("\nNenhum arquivo fornecido via linha de comando.")
        print("Use: python main.py <arquivo1.txt> <arquivo2.txt>\n")

    # exibir resultado final
    for i, tok in enumerate(todos_tokens, 1):
        print(f"\n \n[{i}] {tok}")
