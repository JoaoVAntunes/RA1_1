from auxiliar.Exception import ErroLexico

# ==========================================
# ESTADO INICIAL - DISPATCHER

def estado_inicial(linha, i, lexema, tokens):
    if i >= len(linha):
        #print(f"    [estado_inicial FIM] i={i} >= len={len(linha)}, lexema={repr(lexema)}")
        return estado_inicial, i + 1, lexema, tokens  # Fim da execução
    
    char = linha[i]
    
    # Ignora espaços
    if char in " \t\n":
        return estado_inicial, i + 1, "", tokens
    
    # Números
    if char.isdigit():
        return estado_inteiro, i + 1,char, tokens
    
    # Operadores simples e parênteses
    if char in "+-*%^":
        tokens.append(("OPERADOR", char))
        return estado_inicial, i + 1, "", tokens
    
    if char == "(" or char == ")":
        #print(f"      [estado_inicial] detectou parêntese {repr(char)} em i={i}")
        return estado_parenteses, i, char, tokens
    
    # Divisão (precisa lookahead para // vs /)
    if char == "/":
        return estado_barra, i + 1, char, tokens
    
    # Identificadores e Keywords
    if char == "R":
        return estado_R, i + 1, char, tokens
    elif char.isupper():
        return estado_variavel, i + 1, char, tokens
    
    # Erro léxico
    tokens.append(("ERRO", f"Caractere inválido: {char}", i))
    return estado_erro, i + 1, "", tokens


# ==========================================
# ESTADOS NUMÉRICOS

def estado_inteiro(linha, i, lexema, tokens):
    """Lê um dígito, decide se continua ou passa adiante"""
    if i >= len(linha):
        # Fim da linha - número completo
        tokens.append(("NUMERO", lexema))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char.isdigit():
        # Continua acumulando dígitos
        return estado_inteiro, i + 1, lexema + char, tokens
    
    elif char == ".":
        # Encontrou ponto - vai para decimal
        return estado_ponto, i + 1, lexema + char, tokens
    
    else:
        # Fim do número - sem avançar (lookahead)
        tokens.append(("NUMERO", lexema))
        return estado_inicial, i, "", tokens


def estado_ponto(linha, i, lexema, tokens):
    """Valida que há dígito após o ponto"""
    if i >= len(linha):
        # Ponto no final - erro
        tokens.append(("ERRO", f"Número inválido: {lexema} (ponto sem dígitos)"))
        return estado_erro, i, "", tokens
    
    char = linha[i]
    
    if char.isdigit():
        # Continua com parte decimal
        return estado_decimal, i + 1, lexema + char, tokens
    
    elif char == ".":
        # Ponto duplo - erro
        tokens.append(("ERRO", f"Número inválido: {lexema}. (múltiplos pontos)"))
        return estado_erro, i + 1, "", tokens
    
    else:
        # Ponto sem dígito depois - erro
        tokens.append(("ERRO", f"Número inválido: {lexema} (ponto sem dígitos)"))
        return estado_erro, i, "", tokens


def estado_decimal(linha, i, lexema, tokens):
    """Continua lendo dígitos decimais"""
    if i >= len(linha):
        # Fim da linha - número completo
        tokens.append(("NUMERO", lexema))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char.isdigit():
        # Continua acumulando dígitos decimais
        return estado_decimal, i + 1, lexema + char, tokens
    
    elif char == ".":
        # Ponto duplo - erro
        tokens.append(("ERRO", f"Número inválido: {lexema} (múltiplos pontos)"))
        return estado_erro, i + 1, "", tokens
    
    else:
        # Fim do número - sem avançar (lookahead)
        tokens.append(("NUMERO", lexema))
        return estado_inicial, i, "", tokens


# ==========================================
# ESTADO DE DIVISÃO
# ==========================================
def estado_barra(linha, i, lexema, tokens):
    """Lookahead: verifica se é / ou //"""
    if i >= len(linha):
        # Fim da linha - é só /
        tokens.append(("OPERADOR", "/"))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char == "/":
        # É divisão inteira //
        tokens.append(("OPERADOR", "//"))
        return estado_inicial, i + 1, "", tokens
    
    else:
        # É divisão simples / - sem avançar
        tokens.append(("OPERADOR", "/"))
        return estado_inicial, i, "", tokens


# ==========================================
# ESTADOS DE IDENTIFICADOR E KEYWORDS
# ==========================================

def estado_parenteses(linha, i, lexema, tokens):
    print(f"      [estado_parenteses] lexema={repr(lexema)}, i={i}")
    if lexema == "(":
        tokens.append(("L_PARENTESES", lexema))
        print(f"        -> adicionou token: ('L_PARENTESES', {repr(lexema)})")
    else:
        tokens.append(("R_PARENTESES", lexema))
        print(f"        -> adicionou token: ('R_PARENTESES', {repr(lexema)})")
    return estado_inicial, i + 1, "", tokens


def estado_R(linha, i, lexema, tokens):
    """Pode ser R, RES, ou variável começando com R (ex: RAIO)"""
    if i >= len(linha):
        # Só "R" no final
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char == "E":
        # Pode ser RE ou RES
        return estado_RE, i + 1, lexema + char, tokens
    
    elif char.isupper():
        # Outro maiúsculo - é variável (ex: RAIO)
        return estado_variavel, i + 1, lexema + char, tokens
    
    else:
        # Fim do identificador - é só "R"
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens


def estado_RE(linha, i, lexema, tokens):
    """Pode ser RE, RES, ou variável começando com RE (ex: RESULTADO)"""
    if i >= len(linha):
        # Só "RE" no final
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char == "S":
        # Pode ser RES exata ou REST...
        return estado_RES, i + 1, lexema + char, tokens
    
    elif char.isupper():
        # Outro maiúsculo - é variável (ex: RESULTADO)
        return estado_variavel, i + 1, lexema + char, tokens
    
    else:
        # Fim do identificador - é só "RE"
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens


def estado_RES(linha, i, lexema, tokens):
    """Se continuar com letra, é variável. Se não, é o comando RES"""
    if i >= len(linha):
        # Exatamente "RES" - é o comando
        tokens.append(("COMANDO_RES", "RES"))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char.isupper():
        # Mais uma letra - é variável (ex: RESULTADO, REST)
        return estado_variavel, i + 1, lexema + char, tokens
    
    else:
        # Fim aqui - é a keyword RES
        tokens.append(("COMANDO_RES", "RES"))
        return estado_inicial, i, "", tokens


def estado_variavel(linha, i, lexema, tokens):
    """Acumula qualquer sequência de letras maiúsculas"""
    if i >= len(linha):
        # Fim da linha
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens
    
    char = linha[i]
    
    if char.isupper():
        # Continua acumulando
        return estado_variavel, i + 1, lexema + char, tokens
    
    else:
        # Fim do identificador - sem avançar
        tokens.append(("VARIAVEL", lexema))
        return estado_inicial, i, "", tokens


# ==========================================
# ESTADO DE ERRO
# ==========================================
def estado_erro(linha, i, lexema, tokens):
    if i >= len(linha):
        return estado_inicial, i, "", tokens

    char = linha[i]
    if char in " \t\n()+-*/%^":
        return estado_inicial, i, "", tokens

    raise ErroLexico(f"Caractere inválido: {char}", i)
