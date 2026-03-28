from auxiliar.Exception import ErroLexico

def eh_atribuicao(rpn_tokens):
    """Detecta se a expressão é uma atribuição (último token é VARIAVEL)."""
    return bool(rpn_tokens) and rpn_tokens[-1][0] == 'VARIAVEL'

def converter_para_rpn(tokens):
    """Converte tokens para RPN (preserva postfix e descarta parênteses)."""
    # A sintaxe de entrada já é RPN com parênteses para agrupamento; basta remover parênteses.
    return [tok for tok in tokens if tok[0] not in ('L_PARENTESES', 'R_PARENTESES')]


def avaliar_rpn(rpn_tokens, memoria, resultados):
    """Avalia a expressão em RPN usando stack e memória."""
    stack = []

    for token in rpn_tokens:
        tipo, valor = token

        if tipo == 'NUMERO':
            stack.append(float(valor))

        elif tipo == 'VARIAVEL':
            stack.append(float(memoria.get(valor, 0.0)))    

        elif tipo == 'COMANDO_RES':
            if stack:
                n = int(stack.pop())
                if n <= 0 or n > len(resultados):
                    raise ErroLexico(f'RES inválido: não há {n} resultados anteriores', 'Unknown position')
                stack.append(float(resultados[-n]))
            else:
                if not resultados:
                    stack.append(0.0)
                else:
                    stack.append(float(resultados[-1]))

        elif tipo == 'OPERADOR':
            if len(stack) < 2:
                raise ErroLexico(f'Expressão inválida no operador {valor}', 'Unknown position')

            b = stack.pop()
            a = stack.pop()

            if valor == '+':
                stack.append(a + b)
            elif valor == '-':
                stack.append(a - b)
            elif valor == '*':
                stack.append(a * b)
            elif valor == '/':
                if b == 0:
                    raise ZeroDivisionError('Divisão por zero')
                stack.append(a / b)
            elif valor == '//':
                if b == 0:
                    raise ZeroDivisionError('Divisão inteira por zero')
                stack.append(float(a // b))
            elif valor == '%':
                if b == 0:
                    raise ZeroDivisionError('Resto por zero')
                stack.append(float(a % b))
            elif valor == '^':
                stack.append(float(a ** b))
            else:
                raise ErroLexico(f'Operador desconhecido: {valor}', 'Unknown position')

        else:
            raise ErroLexico(f'Token desconhecido na avaliação RPN: {token}', 'Unknown position')

    if len(stack) != 1:
        raise ErroLexico('Expressão inválida após avaliação RPN', 'Unknown position')

    return float(stack[0])