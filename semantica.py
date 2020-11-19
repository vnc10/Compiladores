from sys import argv
from sintatica2 import Sintatica

class corpoFuncao():
	def __init__(self, tipo, nome, parametros):
		self.tipo = tipo
		self.nome = nome
		self.parametros = parametros
		self.utilizada = 0 
		self.retorno = 0 
		
class No():
	def __init__(self, escopo, tipo, valor, corpo):
		self.escopo = escopo 					
		self.tipo = tipo 						
		self.valor = valor 						
		self.corpo = corpo 				
		self.utilizada = 0 						


class Semantica():

	def __init__(self, code):
		
		self.simbolos = []
		self.funcoes = []
		parser = Sintatica(code)
		self.ast = parser.ast
		self.criaTabelaSimbolos("global", parser.ast)
		self.verificaTipoDoNo("global", parser.ast) 				
		self.verificaFuncaoPrincipal()								
		self.verificaSeFoiUsado()								
		self.verificarRetornos()
		self.imprime()
		

	def andaArvore(self, no):
		while no != None and len(no.filhos) == 1 and no.tipo != "var" and no.tipo != "chamada_funcao":
			no = no.filhos[0]
		return no		

	def criaTabelaSimbolos(self, escopo, no): 
		if no != None:
			if no.tipo == "cabecalho":
				escopo = no.valor
			elif no.tipo == "declaracao_variaveis":
				self.addTabelaSimbolos(escopo, no) 
			elif no.tipo == "parametro":
				self.parametro(escopo, no)
			for filho in no.filhos:
				self.criaTabelaSimbolos(escopo, filho)

	def parametro(self, escopo, no):
		if len(no.filhos) > 0:
			no = No(escopo, no.filhos[0], no.valor, "var")
			self.simbolos.append(no)

	def addTabelaSimbolos(self, escopo, no): 				
		corpo = "var"
		tipo = no.filhos[0].tipo 								
		lv = no.filhos[1]
		vars = self.listaVariaveis(lv, escopo, tipo) 								
		
	def listaVariaveis(self, no, escopo, tipo):
		corpo = "var"
		if(len(no.filhos[0].filhos)> 0):
			if no.filhos[0].filhos[0].tipo == "indice":
				corpo = "array"
			no = No(escopo, tipo, no.filhos[0].valor, corpo)
			self.simbolos.append(no)	
		else:
			no = No(escopo, tipo, no.filhos[0].valor, corpo)
			self.simbolos.append(no)	
			return


	def verificaTipoDoNo(self, escopo, no): 
		if no != None:
			if no.tipo == "cabecalho": 
				escopo = no.valor
			elif no.tipo == "se": 
				self.condicional(no, escopo) 
			elif no.tipo == "atribuicao": 
				self.atribuicao(no, escopo) 
			elif no.tipo == "retorna": 
				self.retorna(escopo, no) 
			elif no.tipo == "chamada_funcao":
				self.chamada_funcao(no, escopo)
			elif no.tipo == "var":
				if len(no.filhos) > 0:
					self.verificarIndiceVetor(no, escopo)
			elif no.tipo == "declaracao_funcao":
				self.declaracaoFuncao(no)

			for filho in no.filhos:
				self.verificaTipoDoNo(escopo, filho)

	def condicional(self, no, escopo): 
		no = no.filhos[0]
		var1 = None
		var2 = None
		if len(no.filhos) == 1:
			no = no.filhos[0]
			var1 = self.andaArvore(no.filhos[0])
			var2 = self.andaArvore(no.filhos[2])
		if var1.tipo == 'var':
			tipo1 = self.procuraNaTabela(var1.valor, escopo)
		else:
			tipo1 = self.getTipoVar(var1.valor)
		if var2.tipo == 'var':
			tipo2 = self.procuraNaTabela(var2.valor, escopo)
		else:
			tipo2 = self.getTipoVar(var2.valor)
		if tipo1 != tipo2:
			print("ERRO: Expressão 'SE' incorreta. Deve comparar dois {}" .format(tipo1))
		if no.filhos[1].tipo != 'operador_relacional':
			print ("Erro: Expressão 'SE' é necessario um operador lógico")

	def declaracaoFuncao(self, no):
		args = []
		if len(no.filhos) > 1:
			nome = no.filhos[1].valor
			tipo = no.filhos[0].tipo
			args = self.cabecalho(no.filhos[1], args)
		else:
			nome = no.filhos[0].valor
			tipo = "vazio"
			args = self.cabecalho(no.filhos[0], args)
		funcao = corpoFuncao(tipo, nome, args)
		self.funcoes.append(funcao)	

	def cabecalho(self, no, args):
		if no == None:
			return []
		if no.filhos[0] != None:
			args = self.lista_parametros(no.filhos[0], args)
			return args

	def atribuicao(self, no, escopo):
		tipos = []

		leftVar = no.filhos[0]
		lefttipo = self.procuraNaTabela(leftVar.valor, escopo)
		tipos.append(lefttipo)

		right = self.andaArvore(no.filhos[1])

		if right.tipo == 'var':
			tipo = self.procuraNaTabela(right.valor, escopo)			
			if tipo == None:
				print ("Erro: Variavel " +  right.filhos[0].valor + " é utilizada, mas não foi declarada")
			else: tipos.append(tipo)

		elif right.tipo == 'numero':
			tipo = self.getTipoVar(right.valor)
			tipos.append(tipo)
	
		if right.tipo == 'expressao_simples':
			tipo_expr = self.expressao_simples(right, escopo)
			tipos.append(tipo_expr)
	
		elif right.tipo == 'expressao_aditiva':
			tipo_expr = self.expressao_aditiva(right, escopo)
			tipos.append(tipo_expr)

		elif right.tipo == 'expressao_multiplicativa':
			tipo_expr = self.expressao_multiplicativa(right, escopo)
			tipos.append(tipo_expr)

		elif right.tipo == 'expressao_unaria':
			tipo_expr = self.expressao_unaria(right, escopo)
			tipos.append(tipo_expr)
	
		for i in range(0, len(tipos)):
			if tipos[0] != tipos[i]:
				if tipos[0] == False or tipos[0] == None:
					aux = tipos[i]
				#else:
					#aux = tipos[0]

				#print ("ERRO: Tipos incompativeis. "+ no.filhos[0].valor +" espera: " + str(aux))

				break

	def expressao_simples(self, no, escopo):	
		if len(no.filhos) == 1:
			folha = self.andaArvore(no)
			if folha.tipo == 'var':
				return self.procuraNaTabela(folha.valor, escopo)
			elif folha.tipo == 'numero':
				return self.getTipoVar(folha.valor)
			elif folha.tipo == 'expressao_aditiva':
				return self.expressao_aditiva(folha, escopo)
			elif folha.tipo == 'expressao_multiplicativa':
				return self.expressao_multiplicativa(folha, escopo)
			elif folha.tipo == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)
		else:
			tipo1 = self.expressao_simples(no.filhos[0], escopo)
			tipo2 = self.expressao_aditiva(no.filhos[2], escopo)
			if tipo1 != tipo2:
				return False 
			else:
				return tipo1 


	def expressao_aditiva(self, no, escopo):
		if len(no.filhos) == 1:
			folha = self.andaArvore(no)

			if folha.tipo == 'var':
				return self.procuraNaTabela(folha.valor, escopo)
			elif folha.tipo == 'numero':
				return self.getTipoVar(folha.valor)
			elif folha.tipo == 'expressao_multiplicativa':
				return self.expressao_multiplicativa(folha, escopo)
			elif folha.tipo == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)
		else:
			tipo1 = self.expressao_aditiva(no.filhos[0], escopo)
			tipo2 = self.expressao_unaria(no.filhos[2], escopo)
			if tipo1 != tipo2:
				return False
			else:
				return tipo1

	def expressao_multiplicativa(self, no, escopo):
		if len(no.filhos) == 1:
			folha = self.andaArvore(no)

			if folha.tipo == 'var':
				return self.procuraNaTabela(folha.valor, escopo)
			elif folha.tipo == 'numero':
				return self.getTipoVar(folha.valor)
			elif folha.tipo == 'expressao_unaria':
				return self.expressao_unaria(folha, escopo)

		else:
			tipo1 = self.expressao_aditiva(no.filhos[0], escopo)
			tipo2 = self.expressao_multiplicativa(no.filhos[2], escopo)

			if tipo1 != tipo2:
				return False
			else:
				return tipo1

	
	def expressao_unaria(self, no, escopo):
		if len(no.filhos) == 1:
			folha = self.andaArvore(no)

			if folha.tipo == 'var':
					return self.procuraNaTabela(folha.valor, escopo)
			elif folha.tipo == 'numero':
					return self.getTipoVar(folha.valor)
		else:
			tipo1 = self.andaArvore(no.filhos[0])
			if tipo1.tipo == 'var':
				return self.procuraNaTabela(tipo1.valor, escopo)
			elif tipo1.tipo == 'numero':
				return self.getTipoVar(tipo1.valor)
	
	def verificaFuncaoPrincipal(self):
		flag = 0
		for funcao in self.funcoes:
			if funcao.nome == "principal":
				flag = 1
		if flag == 0:
			print ("ERRO: Função principal não declarada.")
	
	def verificaSeFoiUsado(self):
		for simbolo in self.simbolos:
			flag = 0
			for simbolo2 in self.simbolos:
				if simbolo.valor == simbolo2.valor and simbolo.escopo == simbolo2.escopo:
					flag = flag + 1
					if flag > 1:
						print ("ERRO: Variável  " + simbolo.valor + " já declarada anteriormente")
						self.simbolos.remove(simbolo)

			if simbolo.utilizada == 0 and flag == 1:
				print ("WARNING: Variável " + simbolo.valor + " declarada e não utilizada")
		


	def verificarRetornos(self):
		for funcao in self.funcoes:
			#if funcao.retorno == 0 and funcao.tipo != "void":
				#print("ERRO: Função " + funcao.nome + " sem retorno. Esperado retornar " + funcao.tipo + ".")
			if funcao.retorno == 0 and funcao.nome == 'principal':
				print("ERRO: Função principal deveria retornar inteiro, mas retorna vazio")

	def procuraNaTabela(self, var, escopo):

		for x in self.simbolos:
			if str(x.valor) == str(var) and str(x.escopo) == str(escopo):
				x.utilizada = 1
				return str(x.tipo)

		for x in self.simbolos:
			if str(x.valor) == str(var) and str(x.escopo) == "global":
				x.utilizada = 1
				return str(x.tipo)
		
		print ("ERRO: Variável " + var + " não declarada.")
		return False
	
	def retorna(self, escopo, no):
		y = self.andaArvore(no)
		tipo = ''
		if y.tipo == "var":
			tipo = self.procuraNaTabela(y.valor, escopo)
		elif y.tipo == "numero":
			tipo = self.getTipoVar(y.valor)
		elif y.tipo == "expressao_simples":
			tipo = self.expressao_simples(y, escopo)
		elif y.tipo == "expressao_aditiva":
			tipo = self.expressao_aditiva(y, escopo)
		elif y.tipo == "expressao_multiplicativa":
			tipo = self.expressao_multiplicativa(y, escopo)
		elif y.tipo == "expressao_unaria":
			tipo = self.expressao_unaria(y, escopo)

		for funcao in self.funcoes:
			if funcao.tipo != tipo and funcao.nome == escopo: 
				print ("ERRO: A função " + escopo + " deve retornar " + funcao.tipo + ".")
				break
			if funcao.tipo == tipo and funcao.nome == escopo:
				funcao.retorno = 1
				break

	def chamada_funcao(self, no, escopo):

		if no.valor == "principal" and escopo == "principal":
			print ("Aviso: Chamada recursiva para a função principal")
			return False

		for i in self.funcoes: 
			l = 0
			if i.nome == no.valor:
				i.utilizada = 1 
				
				l = l + 1
				if no.filhos[0] == None:
					#print("if break ",no.filhos[0])
					return False
				
				args = self.lista_argumentos(no.filhos[0], escopo, [])

				if args != None:
					if len(args) != len(i.parametros) :
						print ("ERRO: Chamada a função " + i.nome + " com número de parâmetros menor que o declarado")
						return False
					#else:
						#for j in range(0,len(args)):
							#if args[j] != i.parametros[j]:
								#print ("ERRO: Tipos incompatíveis no argumento. Argumento " + str(j+1) + " deve ser um " + str(i.parametros[j]) + ". Função " + str(i.nome) + ".")
								#return False
						#return True


		print ("ERRO: Função " + no.valor + " é utilizada mas nao foi declarada.")


	def args_chamadaFunc(self, no, args, escopo):
		if no == None:
			return args

		if len(no.filhos) == 1:
			if no.filhos[0] != None:
				folha = self.andaArvore(no.filhos[0])
				
				if folha.tipo == "var":
					tipo = self.procuraNaTabela(folha.valor, escopo)

					if tipo != None:
						return tipo		

				elif folha.tipo == "numero":
					tipo = self.getTipoVar(folha.valor)
					return tipo
					
		else:
			for filho in no.filhos:
				tipo = self.args_chamadaFunc(filho, args, escopo)
				if tipo == 'inteiro' or tipo == 'flutuante':
					args.append(tipo)

			return args

			
	def lista_parametros(self, no, args):
		for no in no.filhos:
			if no.tipo == "lista_parametros":
				args = self.lista_parametros(no, args)
			y = self.andaArvore(no)			
			if y.tipo != "lista_parametros":
				args.append(y.tipo)
				return args
			else:
				args = self.lista_parametros(y, args)

	def lista_argumentos(self, no, escopo, args):
	

		for no in no.filhos:
			
			if args == None:
				print ("ERRO: Lista de argumentos inválida.")
			y = self.andaArvore(no)
			
			if y.tipo == "expressao_simples":
				tipo = self.expressao_simples(y, escopo)
				if tipo == "flutuante" or tipo == "inteiro":
					args.append(tipo)
					args.append(tipo)
					return args 
			elif y.tipo == "expressao_multiplicativa":
				tipo = self.expressao_multiplicativa(y, escopo)
				if tipo == "flutuante" or tipo == "inteiro":
					args.append(tipo)
					args.append(tipo)
					return args 
			elif y.tipo == "expressao_aditiva":
				tipo = self.expressao_aditiva(y, escopo)
				if tipo == "flutuante" or tipo == "inteiro":
					args.append(tipo)
					args.append(tipo)
					return args 
			elif y.tipo == "expressao_unaria":
				tipo = self.expressao_unaria(y, escopo)
				if tipo == "flutuante" or tipo == "inteiro":
					args.append(tipo)
					args.append(tipo)
					return args 
			elif y.tipo == "var":
				tipo = self.procuraNaTabela(y.valor, escopo)
				args.append(tipo)
			elif y.tipo == "numero":
				tipo = self.getTipoVar(y.valor)
				args.append(tipo)
				return args 
			
			else:
				args = self.lista_argumentos(y,escopo ,args)
			return args


	def getTipoVar(self, num):

		try:
			num = int(num)
		except Exception:
			num = float(num)

		if type(num) == float:
			return "flutuante"
		elif type(num) == int:
			return "inteiro"
			
	
	def verificarIndiceVetor(self, no, escopo):
		y = self.andaArvore(no.filhos[0])
		tipo = ""
		if y.tipo == "var":
			tipo = self.procuraNaTabela(y.valor, escopo)
		elif y.tipo == "numero":
			tipo = self.getTipoVar(y.valor)
		elif y.tipo == "expressao_simples":
			tipo = self.expressao_simples(y, escopo)
		elif y.tipo == "expressao_aditiva":
			tipo = self.expressao_aditiva(y, escopo)
		elif y.tipo == "expressao_multiplicativa":
			tipo = self.expressao_multiplicativa(y, escopo)
		elif y.tipo == "expressao_unaria":
			tipo = self.expressao_unaria(y, escopo)

		if tipo == "flutuante":
			print ("ERRO: Índice do vetor "+ no.valor +" deve ser inteiro.")


	def imprime(self):
		print("Tabela de Simbolos")
		for simbolos in self.simbolos:
			#print("função: , ", simbolos.escopo, simbolos.valor, simbolos.corpo, simbolos.tipo, simbolos.utilizada)
			print(simbolos.escopo, end='')
			print(".", end='')
			print(simbolos.valor, end='')
			print(": ", end='')
			print("[", end='')
			print(simbolos.corpo, end='')
			print(", ", end='')
			print(simbolos.tipo, end='')
			print(", ", end='')
			print(simbolos.utilizada, end='')
			print("]") 
		for funcoes in self.funcoes:
			print("Nome da função: {} \n Tipo: {}".format(funcoes.nome, funcoes.tipo))

if __name__ == '__main__':
	f = open(argv[1])
	semantica = Semantica(f.read())