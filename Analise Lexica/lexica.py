import ply.lex as lex
import sys

class Lexica: 	
    
    def __init__(self):
	    self.lexer = lex.lex(debug=False, module=self, optimize=False)

    reservado = {
        'se': 'SE',
        'senão': 'SENAO',
        'então': 'ENTAO',
        'fim': 'FIM',
        'repita': 'REPITA',
        'até': 'ATE',
        'leia': 'LEIA',
        'escreva': 'ESCREVA',
        'retorna': 'RETORNA',
        'inteiro': 'INTEIRO',
        'flutuante': 'FLUTUANTE',
    }
    
    tokens = [
        'MAIS', 
        'MENOS', 
        'MULTIPLICACAO', 
        'DIVISAO',
        'IGUAL', 
        'DOIS_PONTOS', 
        'VIRGULA', 
        'MENOR', 
        'MAIOR', 
        'DIFERENTE', 
        'MENOR_IGUAL', 
        'MAIOR_IGUAL', 
        'E_LOGICO', 
        'OU_LOGICO', 
        'NEGACAO', 
        'ABRE_PARENTESE', 
        'FECHA_PARENTESE', 
        'ABRE_COLCHETE', 
        'FECHA_COLCHETE', 
        'ATRIBUICAO',
        'ID' 
    ] + list(reservado.values())

    t_ignore = ' \t'
    t_MAIS = r'\+'
    t_MENOS = r'\-'
    t_MULTIPLICACAO = r'\*'
    t_DIVISAO = r'/'
    t_IGUAL = r'\='
    t_DOIS_PONTOS = r'\:'
    t_VIRGULA = r'\,'
    t_MENOR = r'\<'
    t_MAIOR = r'\>'
    t_DIFERENTE = r'\<>'
    t_MENOR_IGUAL = r'\<\='
    t_MAIOR_IGUAL = r'\>\='
    t_E_LOGICO = r'\&\&'
    t_OU_LOGICO = r'\|\|'
    t_NEGACAO = r'\!'
    t_ABRE_PARENTESE = r'\('
    t_FECHA_PARENTESE = r'\)'
    t_ABRE_COLCHETE = r'\['
    t_FECHA_COLCHETE = r'\]'
    t_ATRIBUICAO = r'\:\='

    def t_INTEIRO(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_FLUTUANTE(self, t): 
        r'\d*\.\d+([eE][-+]?\d+)?'
        t.value = float(t.value)
        return t

    def t_COMMENT(self, t):
	    r'\{[^}]*[^{]*\}'
	    for x in xrange(1, len(t.value)):
		    if t.value[x] == "\n":
			    t.lexer.lineno += 1
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ID(self, t):
        r'[A-Za-z_][\w_]*'
        t.type = self.reservado.get(t.value,'ID')
        return t

if __name__ == '__main__':
    code = open(sys.argv[1], encoding='utf8')
    lexer = Lexica()
    lex.input(code.read())
    while True:
        tok = lex.token()
        if not tok:
            break
        print(tok.lineno, ':', tok.type, ':', tok.value)
