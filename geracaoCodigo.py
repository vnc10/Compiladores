from sys import argv
from semantica import Semantica
from llvmlite import ir

class geracaoCodigo():

    def __init__(self, code):
        self.semantica = Semantica(code)
        self.module = ir.Module('meu_modulo.bc')
        arquivo = open('meu_modulo.ll', 'w')
        arquivo.write(str(module))
        arquivo.close()
        print(module)
        

if __name__ == '__main__':
	f = open(argv[1])
	genCode = GenCode(f.read())
		