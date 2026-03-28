#João Vitor de Lima Antunes - JoaoVAntunes
#RA1 1

import sys
from auxiliar.afd import *
from auxiliar.Exception import ErroLexico
from auxiliar.rpn import avaliar_rpn, converter_para_rpn, eh_atribuicao
from auxiliar.validarParenteses import validarBalanceamentoParenteses
from auxiliar.gerador_assembly import gerarAssembly


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
            #print(f"  [LOOP {iteracao}] i={i}, char={repr(char_atual)}, estado={estado.__name__}, lexema={repr(lexema)}")
            estado, i, lexema, vetor_tokens = estado(linha, i, lexema, vetor_tokens)
            print(f"           -> após: i={i}, tokens_count={len(vetor_tokens)}")
        
        #print(f"\n[SAIU DO LOOP] i={i}, len={len(linha)}, estado={estado.__name__}, lexema={repr(lexema)}")
        print(f"[TOKENS ANTES VALIDAÇÃO] {vetor_tokens}")


        validarBalanceamentoParenteses(vetor_tokens)
    
        print("[FIM] Expressão processada com sucesso")

    except ErroLexico as e:
        # Re-lançar para ser tratado pelo chamador
        raise
    

    return vetor_tokens


def executarExpressao(tokens, memoria, resultados):
    """Executa a expressão de tokens e atualiza memória e histórico."""
    if not tokens:
        raise ErroLexico('Nenhum token para executar', 'Unknown position')

    rpn = converter_para_rpn(tokens)

    # Se a expressão termina com VARIAVEL, tenta atribuição
    if eh_atribuicao(rpn):
        var_name = rpn[-1][1]
        
        if len(rpn) == 1:
            # Leitura: (VARIAVEL) - retorna valor da variável sem modificar memória
            valor = float(memoria.get(var_name, 0.0))
            resultados.append(valor)
            return valor
        
        # Tenta avaliar expr_rpn (sem a variável final)
        expr_rpn = rpn[:-1]
        try:
            valor = avaliar_rpn(expr_rpn, memoria, resultados)
            # Sucesso: é atribuição (expr... VARIAVEL)
            memoria[var_name] = valor
            resultados.append(valor)
            return valor
        except ErroLexico:
            # expr_rpn não é expressão válida, trata como expressão normal com variável
            valor = avaliar_rpn(rpn, memoria, resultados)
            resultados.append(valor)
            return valor

    # Sem VARIAVEL no final: avaliação normal (variáveis em qualquer lugar)
    valor = avaliar_rpn(rpn, memoria, resultados)
    resultados.append(valor)
    return valor


def exibirResultados(expressao, valor, eh_atrib=False, var_nome=None):
    if eh_atrib and var_nome:
        print(f'Atribuição em {var_nome}: {valor}')
    else:
        print(f'Resultados para a expressão: {expressao}')
    print(f'Valor calculado: {valor}')


if __name__ == '__main__':
    todos_tokens = []
    memoria = {}
    resultados = []

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

                    rpn_temp = converter_para_rpn(tokens)
                    eh_atrib = eh_atribuicao(rpn_temp)
                    var_nome = rpn_temp[-1][1] if eh_atrib else None

                    valor = executarExpressao(tokens, memoria, resultados)
                    exibirResultados(linha, valor, eh_atrib, var_nome)

                    print(f"\n\nOK: {linha} -> {tokens} -> {valor}")
                except ErroLexico as e:
                    print(f"\n\nERRO: {linha} -> {e.mensagem} (pos {e.posicao})")
                except ZeroDivisionError as e:
                    print(f"\n\nERRO: {linha} -> {e}")
    else:
        print("\nNenhum arquivo fornecido via linha de comando.")
        print("Use: python main.py <arquivo1.txt> <arquivo2.txt>\n")

    # exibir resultado final
    print('\n=== Memória final ===')
    for nome_var, val_var in memoria.items():
        print(f'  {nome_var} = {val_var}')

    print('\n=== Histórico de resultados ===')
    for i, res in enumerate(resultados, 1):
        print(f'  [{i}] {res}')

    # Gerar código Assembly COMPLETO com TODAS as expressões de uma só vez
    if todos_tokens:
        nome_asm = "output.txt"
        try:
            codigo_asm = gerarAssembly(todos_tokens, memoria, resultados, nome_asm)
            print(f'\n[OK] Codigo Assembly salvo em: {nome_asm}')
            print(f'[INFO] Programa contém {len(todos_tokens)} expressão(ões)\n')
        except Exception as e:
            print(f'\n[ERRO] Falha ao gerar Assembly: {e}')

