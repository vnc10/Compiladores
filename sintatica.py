# -*- coding: utf-8 -*-

import ply.yacc as yacc
from lexica import Lexica
from graphviz import Digraph


class Arvore:

	def __init__(self, tipo, filhos=[], valor='', lineno=''):
		self.tipo = tipo
		self.filhos = filhos
		self.valor = valor
		self.lineno = lineno

	def __str__(self):
		return self.tipo


class Sintatica:

	def __init__(self, code):
		lexer = Lexica()
		self.tokens = lexer.tokens
		
		self.precedence = (
                ('left', 'IGUAL', 'MAIOR_IGUAL', 'MAIOR', 'MENOR_IGUAL', 'MENOR'),
                ('left', 'MAIS', 'MENOS'),
                ('left', 'MULTIPLICACAO', 'DIVISAO'),
            )
		parser = yacc.yacc(debug=False, module=self, optimize=False)

		self.ast = parser.parse(code)


	def p_programa(self, p):
		'''
		programa : lista_declaracoes
						'''
		p[0] = Arvore('programa', [p[1]])


	def p_lista_declaracoes(self, p):
		'''
		lista_declaracoes : lista_declaracoes declaracao
							| declaracao		
		'''
		if (len(p) == 3):
			p[0] = Arvore('lista_declaracoes', [p[1], p[2]])

		elif(len(p) == 2):
			p[0] = Arvore('lista_declaracoes', [p[1]])


	def p_declaracao(self, p):
		'''
		declaracao : declaracao_variaveis
					| inicializacao_variaveis
					| declaracao_funcao
		'''
		p[0] = Arvore('declaracao', [p[1]], p.lineno(1))

	
	def p_declaracao_variaveis(self, p):
		'''
		declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis 	
		'''
		p[0] = Arvore('declaracao_variaveis', [p[1], p[3]], p[2])


	def p_inicializacao_variaveis(self, p):
		'''
		inicializacao_variaveis : atribuicao
		'''
		p[0] = Arvore('inicializacao_variaveis', [p[1]])

	
	def p_lista_variaveis(self, p):
		'''
		lista_variaveis : lista_variaveis VIRGULA var
						| var
		'''
		if (len(p) == 4):
			p[0] = Arvore('lista_variaveis', [p[1], p[3]])

		elif(len(p) == 2):
			p[0] = Arvore('lista_variaveis', [p[1]])

	def p_var(self, p):
		'''
		var : ID
				| ID indice
		'''

		if (len(p) == 2):
			h = Arvore('ID', [], p[1], p.lineno(1))
			p[0] = Arvore('var', [h], p[1], p.lineno(1))

		elif(len(p) == 3):
			p[0] = Arvore('var', [p[2]], p[1], p.lineno(1))

	def p_indice(self, p):
		'''
		indice : indice ABRE_COLCHETE expressao FECHA_COLCHETE
						| ABRE_COLCHETE expressao FECHA_COLCHETE
		'''
		if(len(p) == 5):
			p[0] = Arvore('indice', [p[1], p[3]])
		elif(len(p) == 4):
			p[0] = Arvore('indice', [p[2]])
    
	def p_inteiro(self, p):
		'''
		tipo : INTEIRO
		'''
		p[0] = Arvore('inteiro', [], p[1])

	def p_flutuante(self, p):
		'''
		tipo : FLUTUANTE
		'''
		p[0] = Arvore('flutuante', [], p[1])

	def p_declaracao_funcao(self, p):
		'''
		declaracao_funcao : tipo cabecalho
						| cabecalho
		'''

		if len(p) == 3:
			p[0] = Arvore('declaracao_funcao', [p[1], p[2]], p.lineno(2))
		elif len(p) == 2:
			p[0] = Arvore('declaracao_funcao', [p[1]], p.lineno(1))

	

	def p_cabecalho(self, p):
		'''
		cabecalho : ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo FIM
		'''

		p[0] = Arvore('cabecalho', [p[3], p[5]], p[1])



	def p_lista_parametros(self, p):
		'''
		lista_parametros : lista_parametros VIRGULA lista_parametros
							| parametro
		'''

		if len(p) == 4:
			p[0] = Arvore('lista_parametros', [p[1], p[3]])
		elif len(p) == 2:
			p[0] = Arvore('lista_parametros', [p[1]])

	def p_lista_parametros2(self, p):
		'''
		lista_parametros :  vazio
		'''
		# None


	def p_parametro1(self, p):
		'''
		parametro : tipo DOIS_PONTOS ID
		'''

		p[0] = Arvore('parametro', [p[1]], p[3])

	def p_parametro1_error(self, p):
		'''
		parametro : error DOIS_PONTOS ID
		'''
		print("Erro de parâmetro \n")

	def p_parametro2(self, p):
		'''
		parametro : parametro ABRE_COLCHETE FECHA_COLCHETE
		'''
		p[0] = Arvore('parametro', [p[1]])


	def p_corpo(self, p):
		'''
		corpo : corpo acao

		'''

		if len(p) == 3:
			p[0] = Arvore('corpo', [p[1], p[2]])
		elif len(p) == 2:
			p[0] = Arvore('corpo', [p[1]])


	def p_corpo2(self, p):
		'''
		corpo : vazio
		'''

	def p_acao(self, p):
		'''
		acao : expressao
			| declaracao_variaveis
			| se
			| repita
			| leia
			| escreva
			| retorna

		'''

		p[0] = Arvore('acao', [p[1]])

	def p_se(self, p):
		'''
		se : SE expressao ENTAO corpo FIM
				| SE expressao ENTAO corpo SENAO corpo FIM
				| SE ABRE_PARENTESE expressao FECHA_PARENTESE ENTAO corpo SENAO corpo FIM
		'''

		if len(p) == 6: # SE expressao ENTAO corpo FIM
			p[0] = Arvore('se', [p[2], p[4]])
		elif len(p) == 8: # SE expressao ENTAO corpo SENAO corpo FIM
			p[0] = Arvore('se', [p[2], p[4], p[6]])
		elif len(p) == 10: # SE ABRE_PARENTESES expressao FECHA_PARENTESES ENTAO corpo SENAO corpo FIM
			p[0] = Arvore('se', [p[3], p[6], p[8]])


	def p_se2(self, p):
		'''
		se : SE ABRE_PARENTESE expressao FECHA_PARENTESE ENTAO corpo FIM
		'''
		p[0] = Arvore('se', [p[3], p[6]])

	def p_repita(self, p):
		'''
		repita : REPITA corpo ATE expressao
				| REPITA corpo ATE ABRE_PARENTESE expressao FECHA_PARENTESE
		'''
		if len(p) == 5:
			p[0] = Arvore('repita', [p[2], p[4]])
		elif len(p) == 7:
			p[0] = Arvore('repita', [p[2], p[5]])

	def p_atribuicao(self, p):
		'''
		atribuicao : var ATRIBUICAO expressao
		'''
		if len(p):
			p[0] = Arvore('atribuicao', [p[1], p[3]], p[2], p.lineno(2))

	
	def p_leia(self, p):
		'''
		leia : LEIA ABRE_PARENTESE ID FECHA_PARENTESE
		'''
		if len(p):
			p[0] = Arvore('leia', [], p[3],p.lineno(1))



	def p_escreva(self, p):
		'''
		escreva : ESCREVA ABRE_PARENTESE expressao FECHA_PARENTESE
		'''
		p[0] = Arvore('escreva', [p[3]],p.lineno(1))



	def p_retorna(self, p):
		'''
		retorna : RETORNA ABRE_PARENTESE expressao FECHA_PARENTESE
		'''
		p[0] = Arvore('retorna', [p[3]], p.lineno(1))

	def p_expressao(self, p):
		'''
		expressao : expressao_simples
				| atribuicao
		'''
		p[0] = Arvore('expressao', [p[1]])

	
	def p_expressao_simples(self, p):
		'''
		expressao_simples : expressao_aditiva
						| expressao_simples operador_relacional expressao_aditiva
		'''
		if len(p) == 2:
			p[0] = Arvore('expressao_simples', [p[1]])
		elif len(p) == 4:
			p[0] = Arvore('expressao_simples', [p[1], p[2], p[3]])


	def p_expressao_aditiva(self, p):
		'''
		expressao_aditiva : expressao_multiplicativa
						| expressao_aditiva operador_multiplicacao expressao_unaria
		'''
		if len(p) == 2:
			p[0] = Arvore('expressao_aditiva', [p[1]])
		elif len(p) == 4:
			p[0] = Arvore('expressao_aditiva', [p[1], p[2], p[3]])


	def p_expressao_multiplicativa(self, p):
		'''
		expressao_multiplicativa : expressao_unaria
								| expressao_aditiva operador_soma expressao_multiplicativa

		'''
		if len(p) == 2:
			p[0] = Arvore('expressao_multiplicativa', [p[1]])
		elif len(p) == 4:
			p[0] = Arvore('expressao_multiplicativa', [p[1], p[2], p[3]])


	def p_expressao_unaria(self, p):
		'''
		expressao_unaria : fator
						| operador_soma fator

		'''

		if len(p) == 2:
			p[0] = Arvore('expressao_unaria', [p[1]])
		else:
			p[0] = Arvore('expressao_unaria', [p[1], p[2]])


	def p_operador_relacional(self, p):
		'''
		operador_relacional : MENOR
							| MAIOR
							| IGUAL
							| DIFERENTE
							| MENOR_IGUAL
							| MAIOR_IGUAL
							| OU_LOGICO
							| E_LOGICO
		'''

		p[0] = Arvore('operador_relacional', [], str(p[1]), p.lineno(1))

	def p_operador_soma(self, p):
		'''
		operador_soma : MAIS
						| MENOS
		'''
		p[0] = Arvore('operador_soma', [], str(p[1]), p.lineno(1))

	def p_operador_multiplicacao(self, p):
		'''
		operador_multiplicacao : MULTIPLICACAO
								| DIVISAO
		'''
		p[0] = Arvore('operador_multiplicacao', [], str(p[1]))

	def p_fator(self, p):
		'''
		fator : ABRE_COLCHETE  expressao FECHA_COLCHETE
				| var
				| chamada_funcao
				| numero
		'''
		if len(p) == 4:
			p[0] = Arvore('fator', [p[2]])
		else:
			p[0] = Arvore('fator', [p[1]])

	def p_numero_inteiro(self, p):
		"""numero : INTEIRO
			"""
		p[0] = Arvore('inteiro', [], str(p[1]), p.lineno(1))

	def p_numero_flutuante(self, p):
		"""numero : FLUTUANTE
			"""
		p[0] = Arvore('flutuante', [], str(p[1]), p.lineno(1))

	def p_numero_notacao_cientifica(self, p):
		"""numero : NOTACAO_CIENTIFICA
			"""
		p[0] = Arvore('cientifica', [], str(p[1]), p.lineno(1))

	def p_chamada_funcao(self, p):
		'''
		chamada_funcao : ID ABRE_PARENTESE lista_argumentos FECHA_PARENTESE
		'''
		p[0] = Arvore('chamada_funcao', [p[3]], p[1])

	def p_lista_argumentos(self, p):
		'''
		lista_argumentos : lista_argumentos VIRGULA expressao
						| expressao
		'''
		if len(p) == 4:
			p[0] = Arvore('lista_argumentos', [p[1], p[3]])
		else:
			p[0] = Arvore('lista_argumentos', [p[1]])

	def p_lista_argumentos2(self, p):
		'''
		lista_argumentos : vazio
		'''

	def p_vazio(self, p):
		'''
		vazio :
		'''

	def p_indice_error(self, p):
		'''
		indice : indice ABRE_COLCHETE error FECHA_COLCHETE
				| ABRE_COLCHETE error FECHA_COLCHETE
		'''
		print("Erro sintático de indexação \n")


	def p_cabecalho_error(self, p):
		'''
		cabecalho : ID ABRE_PARENTESE error FECHA_PARENTESE error FIM
		'''
		print("Erro no cabeçalho \n")

	def p_se_error(self, p):
		'''
		se : SE error ENTAO error FIM
				| SE error ENTAO error SENAO error FIM
		'''
		print("Erro na expressão se \n")

	def p_repita_error(self, p):
		'''
		repita : REPITA error ATE error
		'''
		print("Erro na expressão repita \n")

	def p_error(self, p):
		if p:
			print("Erro no '%s', na linha %d" % (p.value, p.lineno))
			# exit(1)
		else:
			print(" definições incompletas!")
			#print('Erro sintático: definições incompletas!')
			#exit(1)



class Imprimir():
	def __init__(self):
		self.j = 1
		
	def mostra_Arvore(self,node,strson, father, w, i):
		if node != None :
			i = i + 1
			father = str(node) + " " + str(i-1)+ " " + str(self.j-1)
			for son in node.filhos:
				strson = str(son) + " " + str(i) + " " + str(self.j)
				w.edge(father, strson)
				self.j = self.j + 1
				self.mostra_Arvore(son, strson, father, w, i)




if __name__ == '__main__':
	from sys import argv, exit
	f = open(argv[1])
	try:
		arvore = Sintatica(f.read())
		w = Digraph('G', filename='Saidas/Saida.gv')
		Arvore = Imprimir().mostra_Arvore(arvore.ast,'','', w, i=0)
		
		w.view()

		
	except IOError:
		print ("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.")
		#raise IOError("Erro: Arquivo não encontrado. Verifique se o nome ou diretório está correto.") 
