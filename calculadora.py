 # Yacc example
 
import ply.yacc as yacc
import sys

 # Get the token map from the lexer.  This is required.
from lexica import Lexica

lexica = Lexica()
tokens = lexica.tokens

def p_expression_plus(p):
    'expression : expression MAIS term'
    p[0] = p[1] + p[3]
 
def p_expression_minus(p):
    'expression : expression MENOS term'
    p[0] = p[1] - p[3]
 
def p_expression_term(p):
    'expression : term'
    p[0] = p[1]
 
def p_term_times(p):
    'term : term MULTIPLICACAO factor'
    p[0] = p[1] * p[3]
 
def p_term_div(p):
    'term : term DIVISAO factor'
    p[0] = p[1] / p[3]
 
def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
 
def p_factor_num(p):
    'factor : INTEIRO'
    p[0] = p[1]
 
def p_factor_expr(p):
    'factor : ABRE_PARENTESE expression FECHA_PARENTESE'
    p[0] = p[2]
 
 # Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")
 
 # Build the parser
parser = yacc.yacc()
 
while True:
    try:
       s = input('calc > ')
    except EOFError:
        break
    if not s: continue
    print(s)
    result = parser.parse(s)
    print(result)
