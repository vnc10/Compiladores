from sys import argv, exit

import ply.yacc as yacc
 
# Get the token map from the lexer.  This is required.
from lexica import Lexica


# Verificar como utilizar a anytree. Tem um exportador Dot Graphviz.
from anytree.exporter import DotExporter
from anytree import Node, RenderTree

# Sub-árvore.
#       (programa)
#           |
#   (lista_declaracoes)
#     /     |      \
#   ...    ...     ...


lexica = Lexica()
tokens = lexica.tokens

def p_programa(p):
    "programa : lista_declaracoes"

    global root
    
    father = new_node('Programa')
    root = father
    p[0] = father
    p[1].parent = father


def p_lista_declaracoes(p):
    """lista_declaracoes : lista_declaracoes declaracao
                        | declaracao
    """
    father = new_node('lista_declaracoes')
    p[0] = father
    p[1].parent = father

    #if len(p) > 2:
    #    p[2].parent = father

def p_declaracao(p):
    """declaracao : declaracao_variaveis
                | inicializacao_variaveis
                | declaracao_funcao
    """

# Sub-árvore.
#      (declaracao_variaveis)
#      / p[1]    |           \
# (tipo)    (DOIS_PONTOS)    (lista_variaveis)
#                |
#               (:)

def p_declaracao_variaveis(p):
    "declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis"

 

def p_inicializacao_variaveis(p):
    "inicializacao_variaveis : atribuicao"

def p_lista_variaveis(p):
    """lista_variaveis : lista_variaveis VIRGULA var
                    | var
    """

def p_var(p):
    """var : ID
        | ID indice
    """

def p_indice(p):
    """indice : indice ABRE_COL expressao FECHA_COL
            | ABRE_COL expressao FECHA_COL
    """

def p_indice_error(p):
    """indice : ABRE_COL  error
            | error  FECHA_COL
            | ABRE_COL error FECHA_COL
            | indice ABRE_COL  error
            | indice error  FECHA_COL
            | indice ABRE_COL error FECHA_COL
    """
# Sub-árvore:
#    (tipo)
#      |
#  (FLUTUANTE)
def p_tipo(p):
    """tipo : INTEIRO
        | FLUTUANTE
    """


def p_declaracao_funcao(p):
    """declaracao_funcao : tipo cabecalho 
                        | cabecalho 
    """


def p_cabecalho_error(p):
    """cabecalho : ID error lista_parametros FECHA_PAR corpo FIM
                | ID ABRE_PAR lista_parametros error corpo FIM
                | ID ABRE_PAR lista_parametros FECHA_PAR corpo 
    """

def p_cabecalho(p):
    "cabecalho : ID ABRE_PAR lista_parametros FECHA_PAR corpo FIM"

def p_lista_parametros(p):
    """lista_parametros : lista_parametros VIRGULA parametro
                    | parametro
                    | vazio
    """

def p_parametro(p):
    """parametro : tipo DOIS_PONTOS ID
                | parametro ABRE_COL FECHA_COL
    """

def p_parametro_error(p):
    """parametro : tipo error ID
                | error ID
                | parametro error FECHA_COL
                | parametro ABRE_COL error
    """

def p_corpo(p):
    """corpo : corpo acao
            | vazio
    """


def p_acao(p):
    """acao : expressao
        | declaracao_variaveis
        | se
        | repita
        | leia
        | escreva
        | retorna
    """

def p_se_error(p):
    """se : error expressao ENTAO corpo FIM
        | SE expressao error corpo FIM
        | error expressao ENTAO corpo SENAO corpo FIM
        | SE expressao error corpo SENAO corpo FIM
        | SE expressao ENTAO corpo error corpo FIM
        | SE expressao ENTAO corpo SENAO corpo
    """
    
# Sub-árvore:
#           ___ (SE) ____
#          /      |      \
# (expressao)  (entao)  (senao)
              
def p_se(p):
    """se : SE expressao ENTAO corpo FIM
        | SE expressao ENTAO corpo SENAO corpo FIM
    """
             
def p_repita(p):
    "repita : REPITA corpo ATE expressao"

def p_repita_error(p):
    """repita : error corpo ATE expressao
            | REPITA corpo error expressao
    """
    

def p_atribuicao(p):
    "atribuicao : var ATRIBUICAO expressao"

def p_leia(p):
    "leia : LEIA ABRE_PAR var FECHA_PAR"


def p_leia_error(p):
    """leia : LEIA ABRE_PAR error FECHA_PAR
    """


def p_escreva(p):
    "escreva : ESCREVA ABRE_PAR expressao FECHA_PAR"


def p_retorna(p):
    "retorna : RETORNA ABRE_PAR expressao FECHA_PAR"


def p_expressao(p):
    """expressao : expressao_logica
                | atribuicao
    """

def p_expressao_logica(p):
    """expressao_logica : expressao_simples
                    | expressao_logica operador_logico expressao_simples
    """

def p_expressao_simples(p):
    """expressao_simples : expressao_aditiva
                        | expressao_simples operador_relacional expressao_aditiva
    """

def p_expressao_aditiva(p):
    """expressao_aditiva : expressao_multiplicativa
                        | expressao_aditiva operador_soma expressao_multiplicativa
    """


def p_expressao_multiplicativa(p):
    """expressao_multiplicativa : expressao_unaria
                               | expressao_multiplicativa operador_multiplicacao expressao_unaria
        """


def p_expressao_unaria(p):
    """expressao_unaria : fator
                        | operador_soma fator
                        | operador_negacao fator
        """


def p_operador_relacional(p):
    """operador_relacional : MENOR
                            | MAIOR
                            | IGUALDADE
                            | DIFERENCA 
                            | MENOR_IGUAL
                            | MAIOR_IGUAL
    """

def p_operador_soma(p):
    """operador_soma : ADICAO
                    | SUBTRACAO
    """


def p_operador_logico(p):
    """operador_logico : E_LOGICO
                    | OU_LOGICO
    """


def p_operador_negacao(p):
    "operador_negacao : NEGACAO"


def p_operador_multiplicacao(p):
    """operador_multiplicacao : MULTIPLICACAO
                            | DIVISAO
        """


def p_fator(p):
    """fator : ABRE_PAR expressao FECHA_PAR
            | var
            | chamada_funcao
            | numero
        """

def p_fator_error(p):
    """fator : ABRE_PAR expressao 
    """

def p_numero(p):
    """numero : NUM_INTEIRO
            | NUM_PONTO_FLUTUANTE
            | NUM_NOTACAO_CIENTIFICA
        """

def p_chamada_funcao(p):
    "chamada_funcao : ID ABRE_PAR lista_argumentos FECHA_PAR"

def p_lista_argumentos(p):
    """lista_argumentos : lista_argumentos VIRGULA expressao
                    | expressao
                    | vazio
        """

def p_vazio(p):
    "vazio : "

def p_error(p):

    if p:
        token = p
        print("['{line}','{column}']: erro próximo ao token '{token}'".format(line=token.lineno, column=token.column, token=token.value))

# Programa principal.
def main():
    aux = argv[1].split('.')
    if aux[-1] != 'tpp':
      raise IOError("Not a .tpp file!")
    data = open(argv[1])

    source_file = data.read()
    parser.parse(source_file)

    if root and root.children != ():
        if export_AST:
            print('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * \n')
            print("Generating AST, please wait...")
            DotExporter(root).to_picture("tree.png")
            print("AST was successfully generated.\nOutput file: 'tree.png'")
    else:
        logging.error("Unable to generate AST -- Syntax nodes not found")
    print('\n\n')

# Build the parser.
parser = yacc.yacc(optimize=True, start='programa',debug=True)

if __name__ == "__main__":
    main()