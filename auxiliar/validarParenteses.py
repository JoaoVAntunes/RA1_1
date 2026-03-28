from auxiliar.Exception import ErroLexico


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