from sys import argv
from semantica import Semantica
from llvmlite import ir


class geracaoCodigo(object):
	def __init__(self, code):
		self.semantica = Semantica(code)
		self.arvore = self.semantica.ast
		self.module = ir.Module('meu_modulo.bc')
		self.variaveis = []
		self.variaveisGlobais = []
		self.escopo = "global"
		self.funcs = []
		self.andaArvore(self.arvore)
		self.funcllvm = ''
		self.endBlock = ''
		arquivo = open('meu_modulo.ll', 'w')
		arquivo.write(str(self.module))
		arquivo.close()
		print(self.module)

	def andaArvore(self, no):
		if no != None:
			if no.tipo == 'declaracao_variaveis' and self.escopo == 'global':
				self.variavelGlobal(no)
			if no.tipo == 'declaracao_funcao':
				self.declaracao_funcao(no)
			for filho in no.filhos:
				self.andaArvore(filho)

	def declaracao_funcao(self,no): 
		self.variaveis = self.variaveisGlobais
		args = []
		nomes = []
		if len(no.filhos) > 1: 
			nome = no.filhos[1].valor
			self.escopo = nome 
			if no.filhos[1].filhos[0] is not None:
				args = self.tipoDaFuncao(no.filhos[1].filhos[0], [])
				nomes = self.nomeDaFuncao(no.filhos[1].filhos[0], [])
			tipo = no.filhos[0].tipo 
			if tipo == 'inteiro':
				t_func = ir.FunctionType(ir.IntType(32), (args))
			else:
				t_func = ir.FunctionType(ir.FloatType(), (args))
		else:
			nome = no.filhos[0].valor
			self.escopo = nome
			if no.filhos[0].filhos[0] is not None:
				args = self.tipoDaFuncao(no.filhos[0].filhos[0], [])
				nomes = self.nomeDaFuncao(no.filhos[0].filhos[0], [])
			t_func = ir.FunctionType(ir.VoidType(), (args))
		func = ir.Function(self.module, t_func, nome)
		self.funcs.append(func)
		argumentos_llvm = func.args
		self.funcllvm = func
		entryBlock = func.append_basic_block('entry' + nome)
		builder = ir.IRBuilder(entryBlock)
		for x in range(0,len(argumentos_llvm)): 
			if str(argumentos_llvm[x].tipo) == 'i32':
				var = builder.alloca(ir.IntType(32), name=str(nomes[x]))
				var.align = 4
				self.variaveis.append(var)
			elif str(argumentos_llvm[x].tipo) == 'float':
				var = builder.alloca(ir.FloatType(), name=str(nomes[x]))
				var.align = 4
				self.variaveis.append(var)
		self.redirecionamentoDoNo(no, builder)
		endBasicBlock = func.append_basic_block('exit' + nome)
		self.endBlock = endBasicBlock
		self.retorna(no, builder)
		
	def tipoDaFuncao(self, no, args):
		if(no == 'None'):
			return
		else:
			if(len(no.filhos) > 1):
				for filho in no.filhos:
					if(no == 'None'):
						break
					else:
						args = self.tipoDaFuncao(filho, args)	
			else:
				tipo = no.filhos[0].filhos[0].tipo
				if tipo == 'inteiro':
					args.append(ir.IntType(32))
				elif tipo  == 'flutuante':
					args.append(ir.FloatType())
			return args

	def nomeDaFuncao(self, no, args):
		aux = []
		if len(no.filhos) > 1:
			for filho in no.filhos:
				args = self.nomeDaFuncao(filho, args)
			return args
		else:
			if no.tipo == 'lista_parametros':
				args.append(no.filhos[0].valor)
				return args

	def variavelGlobal(self, no):
		tipo = no.filhos[0].tipo   
		nome = no.filhos[1].filhos[0].valor 
		if tipo == 'inteiro': 
			globalVar = ir.GlobalVariable(self.module, ir.IntType(32), nome)
			globalVar.initializer = ir.Constant(ir.IntType(32), 0)
			globalVar.linkage = 'common'
			globalVar.align = 4
		elif tipo == 'flutuante': 
			globalVar = ir.GlobalVariable(self.module, ir.FloatType(), nome)
			globalVar.initializer = ir.Constant(ir.FloatType(), 0)
			globalVar.linkage = 'common'
			globalVar.align = 4		
		self.variaveisGlobais.append(globalVar)

	def redirecionamentoDoNo(self, no, builder): 
		if no is not None:
			if no.tipo == 'declaracao_variaveis':
				self.declaracao_variavel(no, builder)
			if no.tipo == 'atribuicao':
				self.atribuicao(no, builder)
			if no.tipo == 'se':
				self.se(no, builder)
			if no.tipo == 'repita':
				pass
			if no.tipo == 'chamada_funcao':
				self.chamada_funcao(no, builder)
			if no.tipo == 'escreva':
				self.escreva(no, builder)
			if no.tipo == 'leia':
				self.leia(no, builder)
			else:
				for filho in no.filhos:
					self.redirecionamentoDoNo(filho, builder)

	def retorna(self, no, builder):
		if no is not None:
			pass
			if no.tipo == 'retorna':
				if no.filhos[0].tipo == 'expressao':
					arr = self.expressao(no.filhos[0], [])
					if len(arr) == 1:
						var = self.procuraNaTabela(arr[0])
						if type(var) == int or type(var) == float:
							var = self.cast(var, builder)
						builder.branch(self.endBlock)
						builder.position_at_end(self.endBlock)
						builder.ret(var)
					elif len(arr) == 3:
						var = self.arrayDeExpressoes(builder, arr)
						builder.branch(self.endBlock)
						builder.position_at_end(self.endBlock)
						builder.ret(var)
			else:
				for filho in no.filhos:
					self.retorna(filho, builder)

	def leia(self, no, builder):
		try:
			args_int = [ir.PointerType(ir.IntType(32), 0)]
			leia_int_t = ir.FunctionType(ir.IntType(32), args_int)
			leia_int = ir.Function(self.module, leia_int_t, 'leia_int')
			self.funcs.append(leia_int)
			#float
			args_float = [ir.PointerType(ir.FloatType(), 0)]
			leia_float_t = ir.FunctionType(ir.FloatType(), args_float)
			leia_float = ir.Function(self.module, leia_float_t, 'leia_float')
			self.funcs.append(leia_float)
		except Exception as e:
			pass
		var = self.procuraNaTabela(no.valor)
		args = []
		args.append(var)
		if str(var.tipo) == 'i32*':
			builder.call(self.procuraFunçãoNome('leia_int'), args)
		elif var.tipo == 'float':
			builder.call(self.procuraFunçãoNome('leia_float'), args)

	def escreva(self, no, builder):
		try:
			args = [ir.PointerType(ir.IntType(8), 0)]
			func_t = ir.FunctionType(ir.IntType(32), args, True)
			func = ir.Function(self.module, func_t, 'printf')
		except Exception:
			pass


	def chamada_funcao(self, no, builder):
		if no.filhos[0] is None:
			builder.call(self.procuraFunçãoNome(no.valor), (), no.valor)
		else:
			if no.filhos[0] is not None:
				args_str = []
				args_str = self.lista_argumentos(no.filhos[0], [])
			args_llvm = []
			for arg in args_str:
				print(self.procuraFunçãoNome(no.valor))
				args_llvm.append(builder.load(self.procuraNaTabela(arg), "temp_" + arg))
			builder.call(self.procuraFunçãoNome(no.valor), args_llvm, no.valor)

	def lista_argumentos(self, no, arr):
		if len(no.filhos) > 1:
			for filho in no.filhos:
				arr = self.lista_argumentos(filho, arr)
			return arr
		else:
			aux = []
			if no.tipo == 'lista_argumentos':
				aux = self.expressao(no.filhos[0], aux)

			elif no.tipo == 'expressao':
				aux = self.expressao(no, aux)

			for x in aux:
				arr.append(x)
			return arr

	def declaracao_variavel(self, no, builder):
		tipo = no.filhos[0].tipo
		self.lista_variaveis(no.filhos[1], tipo, builder)

	def lista_variaveis(self, no, tipo, builder):

		if len(no.filhos) == 2: 
			# if len(no.filhos[1].filhos) > 0:
				# if no.filhos[1].filhos[0].tipo == "indice":
					# estrutura = "array"
			
			# no = no(escopo, tipo, no.filhos[1].valor, estrutura)
			# self.lista_variaveis(no.filhos[0], tipo, builder)
			pass
		
		else:
			nome = no.filhos[0].valor
			if tipo == 'inteiro':
				var = builder.alloca(ir.IntType(32), name=nome)
				var.align = 4
				self.variaveis.append(var)

			elif tipo == 'flutuante':
				var = builder.alloca(ir.FloatType(), name=nome)
				var.align = 4
				self.variaveis.append(var)

	def atribuicao(self, no, builder):
		arr = []
		var = no.filhos[0].valor
		arr.append(var)
		if no.filhos[1].tipo == 'expressao':
			arr = self.expressao(no.filhos[1], arr)
		if no.filhos[1].tipo == 'expressao_simples':
			arr = self.expressao_simples(no.filhos[1], arr)
		if no.filhos[1].tipo == 'expressao_aditiva':
			arr = self.expressao_aditiva(no.filhos[1], arr)
		if no.filhos[1].tipo == 'expressao_multiplicativa':
			arr = self.expressao_multiplicativa(no.filhos[1], arr)
		if no.filhos[1].tipo == 'expressao_unaria':
			arr = self.expressao_unaria(no.filhos[1], arr)
		if len(arr) == 2:								
			x = self.procuraNaTabela(arr[0])				
			arr.pop(0)									
			var = self.procuraNaTabela(arr[0])
			var = self.cast(var, builder)
			builder.store(var, x)
		elif len(arr) >= 3: 
			x = self.procuraNaTabela(arr[0]) 
			arr.pop(1)
			temp = self.arrayDeExpressoes(builder, arr)
			builder.store(temp, x) 

	def arrayDeExpressoes(self, builder, arr):
		temp = None
		if len(arr) >= 3:
			operador = arr[1]
			busca = self.procuraNaTabela(arr[0])
			if str(busca.tipo) == ('i32*'):
				var1 = self.procuraNaTabela(arr[0]) 
				var2 = self.procuraNaTabela(arr[2])
				var1 = self.cast(var1, builder) 
				var2 = self.cast(var2, builder)	
				if operador == '+':
					temp = builder.add(var1, var2, name='tempadd', flags=())
				elif operador == '-':
					temp = builder.sub(var1, var2, name='tempsub', flags=())
				elif operador == '/':
					temp = builder.udiv(var1, var2, name='tempdiv', flags=())
				elif operador == '*':
					temp = builder.mul(var1, var2, name='tempmul', flags=())
				return temp
			
			else:
				var1 = self.procuraNaTabela(arr[0]) 
				var2 = self.procuraNaTabela(arr[2])
				var1 = self.cast(var1, builder) 
				var2 = self.cast(var2, builder)	
				if operador == '+':
					temp = builder.fadd(var1, var2, name='tempadd', flags=())
				elif operador == '-':
					temp = builder.fsub(var1, var2, name='tempsub', flags=())
				elif operador == '/':
					temp = builder.fdiv(var1, var2, name='tempdiv', flags=())
				elif operador == '*':
					temp = builder.fmul(var1, var2, name='tempmul', flags=())
				return temp

	def se(self, no, builder):
		arr = self.expressao(no.filhos[0], [])
		if len(no.filhos) == 2:
			predicate = self.funcllvm.append_basic_block('se')
			then = self.funcllvm.append_basic_block('então')
			merge = self.funcllvm.append_basic_block('volta')
			builder.position_at_end(predicate)
			var_cmp = self.procuraNaTabela(arr[0])
			var_cmp2 = self.procuraNaTabela(arr[2])
			var_cmp = self.cast(var_cmp, builder)
			var_cmp2 = self.cast(var_cmp2, builder)
			cmp = builder.icmp_unsigned( arr[1] ,var_cmp, var_cmp2, 'compara')
			builder.select(cmp, then, merge)
			builder.position_at_end(then)
			self.redirecionamentoDoNo(no.filhos[1], builder)
			builder.branch(merge)
			builder.position_at_end(merge)
		else:  
			predicate = self.funcllvm.append_basic_block('se')
			then = self.funcllvm.append_basic_block('então')
			elsee = self.funcllvm.append_basic_block('senão')
			merge = self.funcllvm.append_basic_block('volta')
			builder.position_at_end(predicate)
			var_cmp = self.procuraNaTabela(arr[0])
			var_cmp2 = self.procuraNaTabela(arr[0])
			var_cmp = self.cast(var_cmp, builder)
			var_cmp2 = self.cast(var_cmp2, builder)
			cmp = builder.icmp_unsigned( arr[1] ,var_cmp, var_cmp2, 'compara')
			builder.cbranch(cmp, then, elsee)
			builder.position_at_end(then)
			self.redirecionamentoDoNo(no.filhos[1], builder)
			builder.branch(merge)
			builder.position_at_end(elsee)
			self.redirecionamentoDoNo(no.filhos[2], builder)
			builder.branch(merge)
			builder.position_at_end(merge)		

	def procuraNaTabela(self, var):
		for x in self.variaveis:
			if x.name == str(var):
				return x
		try:
			var = int(var)
			return var
		except Exception as e:
			try:
				var = float(var)
				return var
			except Exception as e:
				pass

	def cast(self, var, builder): 
		if type(var) == int:
			num = ir.Constant(ir.IntType(32), var)
			return num
		elif type(var) == float:
			num = ir.Constant(ir.FloatType(), var)
			return num
		else:
			load = builder.load(var, name='')
			return load
			

	def stringToNumber(self, x):
		try:
			x = int(x)
			return x
		except Exception as e:
			try:
				x = float(x)
				return x
			except Exception as e:
				pass

	def procuraFunçãoNome(self, nome):
		for function in self.funcs:
			if function.name == nome:
				return function

	def expressao(self, no, arr):
		if no.filhos[0].tipo == 'expressao_simples':
			self.expressao_simples(no.filhos[0], arr)
			return arr
		else:
			pass

	def expressao_simples(self, no, arr):
		if len(no.filhos) == 1:
			self.expressao_aditiva(no.filhos[0],arr)
			return arr
		else:
			arr = self.expressao_simples(no.filhos[0], arr)
			arr = self.operador_relacional(no.filhos[1], arr)
			arr = self.expressao_aditiva(no.filhos[2], arr)
			return arr

	def expressao_aditiva(self, no, arr):
		if len(no.filhos) == 1:
			self.expressao_multiplicativa(no.filhos[0], arr)
			return arr
		else:
			arr = self.expressao_aditiva(no.filhos[0], arr)
			arr  = self.operador_multiplicacao(no.filhos[1], arr)
			arr = self.expressao_unaria(no.filhos[2], arr)
			return arr

	def expressao_multiplicativa(self, no,arr):
		if len(no.filhos) == 1:
			arr = self.expressao_unaria(no.filhos[0], arr)			
			return arr
		else:
			arr = self.expressao_aditiva(no.filhos[0], arr)
			arr = self.operador_soma(no.filhos[1], arr)
			arr = self.expressao_multiplicativa(no.filhos[2], arr)
			return arr

	def expressao_unaria(self, no, arr):
		if len(no.filhos) == 1:
			arr = self.fator(no.filhos[0], arr)
			return arr
		else:
			arr = self.operador_soma(no.filhos[0], arr)
			arr = self.fator(no.filhos[1], arr)
			return arr
			
	def operador_relacional(self, no, arr):
		arr.append(no.valor)
		return arr

	def operador_soma(self, no, arr):
		arr.append(no.valor)
		return arr

	def operador_multiplicacao(self, no, arr):
		arr.append(no.valor)
		return arr

	def fator(self,no, arr):
		if len(no.filhos) == 1:
			if no.filhos[0].tipo == 'var':
				arr.append(no.filhos[0].valor)
				return arr
			elif no.filhos[0].tipo == 'numero':
				arr.append(no.filhos[0].valor)	
				return arr

if __name__ == '__main__':
	f = open(argv[1])
	geracaoCodigo = geracaoCodigo(f.read())
		