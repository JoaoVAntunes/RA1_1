# Gerador de Assembly ARMv7 para expressões RPN
# Entrada: tokens do analisador léxico
# Saída: código Assembly compatível com Cpulator-ARMv7 DEC1-SOC v16.1

from auxiliar.Exception import ErroLexico

class GeradorAssembly:
    def __init__(self):
        self.asm_code = []
        self.constantes = {}  # {valor_float: label}
        self.num_constantes = 0
        self.stack_ptr = 0  # Controla d0-d7
        self.memoria_vars = {}  # {nome_var: endereco_memoria}
        self.num_vars = 0
        self.num_expressoes = 0  # Contador para nomes de buffers de resultado
        self.labels_resultado = []  # Lista de labels de resultado gerados
        
    def gerar_label_constante(self, valor):
        """Gera label único para constante e armazena."""
        if valor not in self.constantes:
            label = f"const_{self.num_constantes}"
            self.constantes[valor] = label
            self.num_constantes += 1
        return self.constantes[valor]
    
    def gerar_label_variavel(self, nome_var):
        """Gera/obtém label para variável MEM."""
        if nome_var not in self.memoria_vars:
            label = f"var_{nome_var}"
            self.memoria_vars[nome_var] = label
            self.num_vars += 1
        return self.memoria_vars[nome_var]
    
    def registrador_disponivel(self):
        """Retorna registrador d disponível (d0-d7)."""
        if self.stack_ptr < 8:
            reg = f"d{self.stack_ptr}"
            self.stack_ptr += 1
            return reg
        else:
            raise ErroLexico("Stack de registradores VFP cheio (máximo 8)", "Unknown position")
    
    def limpar_codigo(self):
        """Limpa self.asm_code para nova geração."""
        self.asm_code = []
        self.stack_ptr = 0
    
    def gerar_label_resultado(self):
        """Gera label único para resultado de expressão."""
        label = f"result_{self.num_expressoes}"
        self.labels_resultado.append(label)
        self.num_expressoes += 1
        return label
    
    def processar_tokens_rpn(self, tokens, memoria_dict, resultados_list):
        """
        Processa uma única expressão RPN e gera código Assembly para ela.
        Reseta stack_ptr mas acumula em asm_code.
        
        memoria_dict: dicionário de variáveis (de executarExpressao)
        resultados_list: histórico de resultados (de executarExpressao)
        Retorna: label do buffer de resultado para esta expressão
        """
        self.stack_ptr = 0  # Reset apenas do stack_ptr
        codigo_expr = []
        
        stack_simulada = []
        
        for token in tokens:
            tipo, valor = token
            
            if tipo == 'NUMERO':
                # Carregar número como constante
                label = self.gerar_label_constante(float(valor))
                reg = self.registrador_disponivel()
                codigo_expr.append(f"    ldr r0, ={label}")
                codigo_expr.append(f"    vldr {reg}, [r0]")
            
            elif tipo == 'OPERADOR':
                # Aplicar operação
                # O resultado vai no registrador do primeiro operando
                if self.stack_ptr < 2:
                    raise ErroLexico(f"Insuficientes valores no stack para operação {valor}", "Unknown position")
                
                d_src2 = f"d{self.stack_ptr - 1}"  # Segundo operando (topo)
                d_src1 = f"d{self.stack_ptr - 2}"  # Primeiro operando
                d_dst = d_src1  # Resultado vai onde estava o primeiro operando
                
                if valor == '+':
                    codigo_expr.append(f"    vadd.f64 {d_dst}, {d_src1}, {d_src2}")
                elif valor == '-':
                    codigo_expr.append(f"    vsub.f64 {d_dst}, {d_src1}, {d_src2}")
                elif valor == '*':
                    codigo_expr.append(f"    vmul.f64 {d_dst}, {d_src1}, {d_src2}")
                elif valor == '/':
                    codigo_expr.append(f"    vdiv.f64 {d_dst}, {d_src1}, {d_src2}")
                elif valor == '//':
                    # Divisão inteira
                    codigo_expr.append(f"    vcvt.s32.f64 s0, {d_src1}")
                    codigo_expr.append(f"    vcvt.s32.f64 s1, {d_src2}")
                    codigo_expr.append(f"    sdiv r0, r1")
                    codigo_expr.append(f"    vcvt.f64.s32 {d_dst}, s0")
                elif valor == '%':
                    # Resto
                    codigo_expr.append(f"    vcvt.s32.f64 s0, {d_src1}")
                    codigo_expr.append(f"    vcvt.s32.f64 s1, {d_src2}")
                    codigo_expr.append(f"    sdiv r0, r1")
                    codigo_expr.append(f"    mls r0, r0, r2, r1")
                    codigo_expr.append(f"    vcvt.f64.s32 {d_dst}, s0")
                elif valor == '^':
                    codigo_expr.append(f"    ; Potência (^ não implementada)")
                
                # Remove um elemento do stack (o segundo operando)
                self.stack_ptr -= 1
            
            elif tipo == 'VARIAVEL':
                # Carregar variável
                label = self.gerar_label_variavel(valor)
                reg = self.registrador_disponivel()
                codigo_expr.append(f"    ldr r0, ={label}")
                codigo_expr.append(f"    vldr {reg}, [r0]")
            

            elif tipo == 'COMANDO_RES':
                if self.stack_ptr < 1:
                    raise ErroLexico("RES requer número anterior", "Unknown position")

                self.stack_ptr -= 1
                d_index = f"d{self.stack_ptr}"

            

                if not resultados_list:
                    raise ErroLexico("RES sem histórico de resultados", "Unknown position")

                n = int(resultados_list[-1]) if resultados_list else 1

                if n <= 0 or n > len(resultados_list):
                    raise ErroLexico(f"RES inválido: {n}", "Unknown position")

                valor = float(resultados_list[-n])
                label = self.gerar_label_constante(valor)

                reg = self.registrador_disponivel()

                codigo_expr.append(f"    @ RES ({n})")
                codigo_expr.append(f"    ldr r0, ={label}")
                codigo_expr.append(f"    vldr {reg}, [r0]")
        
        # Resultado final está em d0
        if self.stack_ptr != 1:
            raise ErroLexico(f"Expressão RPN inválida (stack final: {self.stack_ptr})", "Unknown position")
        
        # Gerar label para esta expressão e acumular código
        label_resultado = self.gerar_label_resultado()
        
        # Adicionar comentário e instruções de armazenamento
        self.asm_code.append(f"    @ Expressão {self.num_expressoes - 1}")
        self.asm_code.extend(codigo_expr)
        self.asm_code.append(f"    ldr r0, ={label_resultado}")
        self.asm_code.append(f"    vstr d0, [r0]")
        self.asm_code.append("")
        
        return label_resultado
    
    def gerar_secao_dados(self):
        """Gera seção .data com constantes, variáveis, buffers de resultado."""
        lines = [".data"]
        
        # Constantes
        for valor, label in self.constantes.items():
            lines.append(f"    {label}: .double {valor}")
        
        # Variáveis MEM
        for nome_var, label in self.memoria_vars.items():
            lines.append(f"    {label}: .double 0.0")
        
        # Histórico de resultados
        lines.append(f"    result_history: .space 800  @ 100 doubles")
        lines.append(f"    result_count: .word 0")
        
        # Buffers de resultado (um por expressão)
        for label in self.labels_resultado:
            lines.append(f"    {label}: .space 8")
        
        return lines
    
    def gerar_programa_completo(self, tokens, memoria_dict, resultados_list, nome_funcao="main"):
        """Gera programa Assembly completo com seção .text e .data consolidadas.
        
        Compatível com chamadas antigas (tokens único).
        """
        # Detectar se é lista de listas ou lista simples
        if tokens and isinstance(tokens[0], (list, tuple)):
            # É lista de listas - múltiplas expressões
            return self._gerar_multiplas_expressoes(tokens, memoria_dict, resultados_list, nome_funcao)
        else:
            # É lista simples - expressão única (compatibilidade)
            return self._gerar_programa_unico(tokens, memoria_dict, resultados_list, nome_funcao)
    
    def _gerar_programa_unico(self, tokens, memoria_dict, resultados_list, nome_funcao="main"):
        """Gera programa Assembly para uma única expressão."""
        programa = []
        self.limpar_codigo()
        programa.append(".global " + nome_funcao)
        programa.append(nome_funcao + ":")
        programa.append("    push {r4-r11, lr}")
        programa.append("    sub sp, sp, #8")
        programa.append("")
        
        # Processar uma expressão
        self.processar_tokens_rpn(tokens, memoria_dict, resultados_list)
        programa.extend(self.asm_code)
        
        # Epilogo corrigido (evita loop infinito no CPulator)
        programa.append("    add sp, sp, #8")
        programa.append("    pop {r4-r11, lr}")
        programa.append("    b end")
        programa.append("end: b end")
        programa.append("")
        
        # Seção de dados - UMA ÚNICA VEZ
        programa.extend(self.gerar_secao_dados())
        
        return "\n".join(programa)
    
    def _gerar_multiplas_expressoes(self, lista_tokens, memoria_dict, resultados_list, nome_funcao="main"):
        """Gera programa Assembly para múltiplas expressões."""
        programa = []
        self.limpar_codigo()
        self.num_expressoes = 0  # Reset contador de expressões
        
        programa.append(".global " + nome_funcao)
        programa.append(nome_funcao + ":")
        programa.append("    push {r4-r11, lr}")
        programa.append("    sub sp, sp, #8")
        programa.append("")
        
        # Processar cada expressão
        for idx, tokens in enumerate(lista_tokens):
            try:
                self.processar_tokens_rpn(tokens, memoria_dict, resultados_list)
            except ErroLexico as e:
                raise ErroLexico(f"Expressão {idx}: {e.mensagem}", e.posicao)
        
        programa.extend(self.asm_code)
        
        # Epilogo corrigido (evita loop infinito no CPulator)
        programa.append("    add sp, sp, #8")
        programa.append("    pop {r4-r11, lr}")
        programa.append("    b end")
        programa.append("end: b end")
        programa.append("")
        
        # Seção de dados - UMA ÚNICA VEZ
        programa.extend(self.gerar_secao_dados())
        
        return "\n".join(programa)


def gerarAssembly(tokens_list, memoria=None, resultados=None, nome_arquivo="output.txt"):
    """
    Função principal para gerar Assembly.
    
    Parâmetros:
    - tokens_list: lista de listas de tokens (uma por expressão) OU lista simples (compatibilidade)
    - memoria: dicionário de variáveis (do executarExpressao)
    - resultados: lista de resultados (do executarExpressao)
    - nome_arquivo: nome do arquivo .s a salvar
    
    Retorna: código Assembly como string
    """
    if memoria is None:
        memoria = {}
    if resultados is None:
        resultados = []
    
    gerador = GeradorAssembly()
    codigo_asm = gerador.gerar_programa_completo(tokens_list, memoria, resultados)
    
    # Salvar em arquivo
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(codigo_asm)
    except IOError as e:
        print(f"Erro ao salvar Assembly: {e}")
    
    return codigo_asm
