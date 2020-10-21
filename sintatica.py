import ply.yacc as yacc
from lexica import Lexica
from graphviz import Digraph
from sys import argv


class Tree:
    def __init__(self, type_node='', child=[], value='', line=''):
        self.type = type_node
        self.child = child
        self.value = value
        self.line = line

    def __str__(self):
        return self.type

class Sintatica:
    
    def __init__(self, code):
        lexica = Lexica()
        self.tokens = lexica.tokens
        self.precedence = (
            ('left', 'IGUAL', 'MAIOR_IGUAL', 'MAIOR', 'MENOR_IGUAL', 'MENOR'),
            ('left', 'MAIS', 'MENOS'),
            ('left', 'MULTIPLICACAO', 'DIVISAO'),
        )
        parser = yacc.yacc(debug=False, module=self, optimize=False)
        self.ast = parser.parse(code)
    
    def p_programa(self, p):
        "programa : lista_declaracoes"
            
        p[0] = Tree('programa', [p[1]])

    def p_lista_declaracoes(self, p):
        """lista_declaracoes : lista_declaracoes declaracao
                            | declaracao
        """
        if len(p) == 3:
            p[0] = Tree('lista_declaracoes', [p[1], p[2]])
        else:
            p[0] = Tree('lista_declaracoes', [p[1]])

    def p_declaracao(self, p):
        """declaracao : declaracao_variaveis
                    | inicializacao_variaveis
                    | declaracao_funcao
        """
        p[0] = Tree('declaracao', [p[1]], p.lineno(1))

    def p_declaracao_variaveis(self, p):
        "declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis"
        p[0] = Tree('declaracao_variaveis', [p[1], p[3]], p[2])
    

    def p_inicializacao_variaveis(self, p):
        "inicializacao_variaveis : atribuicao"

        p[0] = Tree('inicializacao_variaveis', [p[1]])

    def p_lista_variaveis(self, p):
        """lista_variaveis : lista_variaveis VIRGULA var
                        | var
        """

        if (len(p) == 4):
            p[0] = Tree('lista_variaveis', [p[1], p[3]])
        elif(len(p) == 2):
            p[0] = Tree('lista_variaveis', [p[1]])

    def p_var(self, p):
        """var : ID
            | ID indice
        """
        if (len(p) == 2):
            h = Tree('ID', [], p[1], p.lineno(1))
            p[0] = Tree('var', [h], p[1], p.lineno(1))
        elif(len(p) == 3):
            p[0] = Tree('var', [p[2]], p[1], p.lineno(1))

    def p_indice(self, p):
        """indice : indice ABRE_COLCHETE expressao FECHA_COLCHETE
                | ABRE_COLCHETE expressao FECHA_COLCHETE
        """
        if(len(p) == 5):
            p[0] = Tree('indice', [p[1], p[3]])
        elif(len(p) == 4):
            p[0] = Tree('indice', [p[2]])
        

    def p_indice_error(self, p):
        """indice : ABRE_COLCHETE  error
                | error  FECHA_COLCHETE
                | ABRE_COLCHETE error FECHA_COLCHETE
                | indice ABRE_COLCHETE  error
                | indice error  FECHA_COLCHETE
                | indice ABRE_COLCHETE error FECHA_COLCHETE
        """
        
        print("Erro sintático de indexação \n")


    def p_tipo(self, p):
        '''tipo : INTEIRO
        | FLUTUANTE'''

        p[0] = Tree('tipo', [], p[1])


    def p_declaracao_funcao(self, p):
        """declaracao_funcao : tipo cabecalho 
                            | cabecalho 
        """
        if len(p) == 3:
            p[0] = Tree('declaracao_funcao', [p[1], p[2]], p.lineno(2))
        elif len(p) == 2:
            p[0] = Tree('declaracao_funcao', [p[1]], p.lineno(1))



    def p_cabecalho_error(self, p):
        """cabecalho : ID error lista_parametros FECHA_PARENTESE corpo FIM
                    | ID ABRE_PARENTESE lista_parametros error corpo FIM
                    | ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo 
        """
        print("Erro no cabeçalho \n")

    def p_cabecalho(self, p):
        "cabecalho : ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo FIM"

        p[0] = Tree('cabecalho', [p[3], p[5]], p[1])

    def p_lista_parametros(self, p):
        """lista_parametros : lista_parametros VIRGULA parametro
                        | parametro
                        | vazio
        """
        if len(p) == 4:
            p[0] = Tree('lista_parametros', [p[1], p[3]])
        elif len(p) == 2:
            p[0] = Tree('lista_parametros', [p[1]])

    def p_parametro(self, p):
        """parametro : tipo DOIS_PONTOS ID
                    | parametro ABRE_COLCHETE FECHA_COLCHETE
        """
        p[0] = Tree('parametro', [p[1]], p[3])
        p[0] = Tree('parametro', [p[1]])

    def p_parametro_error(self, p):
        """parametro : tipo error ID
                    | error ID
                    | parametro error FECHA_COLCHETE
                    | parametro ABRE_COLCHETE error
        """
        print("Erro de parâmetro \n")

    def p_corpo(self, p):
        """corpo : corpo acao
                | vazio
        """
        if len(p) == 3:
            p[0] = Tree('corpo', [p[1], p[2]])
        elif len(p) == 2:
            p[0] = Tree('corpo', [p[1]])


    def p_acao(self, p):
        """acao : expressao
            | declaracao_variaveis
            | se
            | repita
            | leia
            | escreva
            | retorna
        """
        p[0] = Tree('acao', [p[1]])

    def p_se_error(self, p):
        """se : error expressao ENTAO corpo FIM
            | SE expressao error corpo FIM
            | error expressao ENTAO corpo SENAO corpo FIM
            | SE expressao error corpo SENAO corpo FIM
            | SE expressao ENTAO corpo error corpo FIM
            | SE expressao ENTAO corpo SENAO corpo
        """
        print("Erro na expressão Se \n")
                
    def p_se(self, p):
        """se : SE expressao ENTAO corpo FIM
            | SE expressao ENTAO corpo SENAO corpo FIM
        """
        if len(p) == 6:
            p[0] = Tree('se', [p[2], p[4], Tree(type_node=p[5])])
        else:
            p[0] = Tree('se', [p[2], p[4], p[6], Tree(type_node=p[7])])

                
    def p_repita(self, p):
        "repita : REPITA corpo ATE expressao"
        if len(p) == 5:
            p[0] = Tree('repita', [p[2], p[4]])
        elif len(p) == 7:
            p[0] = Tree('repita', [p[2], p[5]])

    def p_repita_error(self, p):
        """repita : error corpo ATE expressao
                | REPITA corpo error expressao
        """
        print("Erro na expressão repita \n")
        

    def p_atribuicao(self, p):
        "atribuicao : var ATRIBUICAO expressao"
        if len(p):
            p[0] = Tree('atribuicao', [p[1], p[3]], p[2], p.lineno(2))

    def p_leia(self, p):
        "leia : LEIA ABRE_PARENTESE var FECHA_PARENTESE"
        if len(p):
            p[0] = Tree('leia', [], p[3],p.lineno(1))


    def p_leia_error(self, p):
        """leia : LEIA ABRE_PARENTESE error FECHA_PARENTESE
        """
        print("Erro na expressão LEIA \n")


    def p_escreva(self, p):
        "escreva : ESCREVA ABRE_PARENTESE expressao FECHA_PARENTESE"
        p[0] = Tree('escreva', [p[3]],p.lineno(1))


    def p_retorna(self, p):
        "retorna : RETORNA ABRE_PARENTESE expressao FECHA_PARENTESE"
        p[0] = Tree('retorna', [p[3]], p.lineno(1))


    def p_expressao(self, p):
        """expressao : expressao_logica
                    | atribuicao
        """
        p[0] = Tree('expressao', [p[1]])

    def p_expressao_logica(self, p):
        """expressao_logica : expressao_simples
                        | expressao_logica operador_logico expressao_simples
        """
        if len(p) == 2:
            p[0] = Tree('expressao_logica', [p[1]])
        else:
            p[0] = Tree('expressao_logica', [p[1], p[2], p[3]])

    def p_expressao_simples(self, p):
        """expressao_simples : expressao_aditiva
                            | expressao_simples operador_relacional expressao_aditiva
        """
        if len(p) == 2:
            p[0] = Tree('expressao_simples', [p[1]])
        elif len(p) == 4:
            p[0] = Tree('expressao_simples', [p[1], p[2], p[3]])

    def p_expressao_aditiva(self, p):
        """expressao_aditiva : expressao_multiplicativa
                            | expressao_aditiva operador_soma expressao_multiplicativa
        """
        if len(p) == 2:
            p[0] = Tree('expressao_aditiva', [p[1]])
        elif len(p) == 4:
            p[0] = Tree('expressao_aditiva', [p[1], p[2], p[3]])


    def p_expressao_multiplicativa(self, p):
        """expressao_multiplicativa : expressao_unaria
                                | expressao_multiplicativa operador_multiplicacao expressao_unaria
            """
        if len(p) == 2:
            p[0] = Tree('expressao_multiplicativa', [p[1]])
        elif len(p) == 4:
            p[0] = Tree('expressao_multiplicativa', [p[1], p[2], p[3]])

    def p_expressao_unaria(self, p):
        """expressao_unaria : fator
                            | operador_soma fator
                            | operador_negacao fator
            """
        if len(p) == 2:
            p[0] = Tree('expressao_unaria', [p[1]])
        else:
            p[0] = Tree('expressao_unaria', [p[1], p[2]])


    def p_operador_relacional(self, p):
        """operador_relacional : MENOR
                                | MAIOR
                                | IGUAL
                                | DIFERENTE 
                                | MENOR_IGUAL
                                | MAIOR_IGUAL
        """
        p[0] = Tree('operador_relacional', [], str(p[1]), p.lineno(1))

    def p_operador_soma(self, p):
        """operador_soma : MAIS
                        | MENOS
        """
        p[0] = Tree('operador_soma', [], str(p[1]), p.lineno(1))


    def p_operador_logico(self, p):
        """operador_logico : E_LOGICO
                        | OU_LOGICO
        """
        p[0] = Tree('operador_logico', [], str(p[1]))

    def p_operador_negacao(self, p):
        """operador_negacao : NEGACAO
        """
        p[0] = Tree('operador_negacao', [], str(p[1]), p.lineno(1))

    def p_operador_multiplicacao(self, p):
        """operador_multiplicacao : MULTIPLICACAO
                                | DIVISAO
            """
        p[0] = Tree('operador_multiplicacao', [], str(p[1]))

    def p_fator(self, p):
        """fator : ABRE_PARENTESE expressao FECHA_PARENTESE
                | var
                | chamada_funcao
                | numero
            """
        if len(p) == 4:
            p[0] = Tree('fator', [p[2]])
        else:
            p[0] = Tree('fator', [p[1]])


    def p_numero(self, p):
        """numero : INTEIRO
                | FLUTUANTE
                | NOTACAO_CIENTIFICA
            """
        p[0] = Tree('numero', [], str(p[1]), p.lineno(1))

    def p_chamada_funcao(self, p):
        "chamada_funcao : ID ABRE_PARENTESE lista_argumentos FECHA_PARENTESE"
        p[0] = Tree('chamada_funcao', [p[3]], p[1])

    def p_lista_argumentos(self, p):
        """lista_argumentos : lista_argumentos VIRGULA expressao
                        | expressao
                        | vazio
            """
        if len(p) == 4:
            p[0] = Tree('lista_argumentos', [p[1], p[3]])
        else:
            p[0] = Tree('lista_argumentos', [p[1]])

    def p_vazio(self, p):
        "vazio : "
    
    def p_error(self , p):

        if p:
            print("Erro no '%s', na linha: %d" % (p.value, p.lineno))

class Print():
    def __init__(self):
        self.j = 1    

    def printTree(self, node, sizeSon, father, w, i):
        j = 1
        if node != None :
            i = i + 1
            father = str(node) + " " + str(i-1) + " " + str(self.j-1)
            for son in node.child:
                sizeSon = str(son) + " " + str(i) + " " + str(self.j)
                w.edge(father, sizeSon)
                self.j = self.j + 1
                self.printTree(son, sizeSon, father, w, i)




if __name__ == '__main__':
    f = open(argv[1])
arvore = Sintatica(f.read())
w = Digraph('G', filename='PDF/Arvore')
tree = Print().printTree(arvore.ast,'','', w, i=0)
w.view() 
