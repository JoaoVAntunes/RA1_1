# exception.py

class ErroLexico(Exception):
    """Erro na tokenização (AFD)"""
    def __init__(self, mensagem, posicao):
        self.mensagem = mensagem
        self.posicao = posicao
        super().__init__(f"[{posicao}] {mensagem}")
