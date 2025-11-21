#0.1
"""
PRINCIPAIS PONTOS NECESSÁRIOS:
INTERFACE DO BROWSER
FUNÇÕES PARA LIGAR OS MÉTODOS AOS COMANDOS COM #
"""
"""
O QUE JÁ TEMOS:
BASE DO NAVEGADOR
FUNÇÃO BACK PRA VOLTAR PRA PÁGINA ANTERIOR
FUNÇÃO SAIR PRA ENCERRAR A NAVEGAÇÃO
"""

class Site_atual:
  def __init__(self, carga=0, prox=None):
    self.carga = carga
    self.prox = prox

  def __repr__(self):
    return '%s/%s' % (self.carga, self.prox)

class Navegador:
  def __init__(self):
    self.topo = None #URL inicial, começa vazia, logicamente
    self.contador = 0 #apenas simbólico pra contar qnts URL's foram acessadas

  def is_empty(self):
     return self.topo is None

  def push(self, elemento): #vai adicionar urls no topo da
     site = Site_atual(elemento)
     site.prox = self.topo
     self.topo = site
     self.contador += 1

  def pop(self): #vai excluir o ultimo URL, o atual no caso.
  #Esse é o método que tem que ligar em uma função para usar o #back
    assert self.topo != None, "Nenhuma página anterior"
    self.topo = self.topo.prox #transforma a URL atual na anterior a ela
    self.contador -= 1
    if self.topo != None:
      return self.topo.carga
    return "Página inicial" #Se não exixtir nenhuma página antes

  def encerrar(self): #colocar esse método com a função de #sair
    return 'NAVEGAÇÃO ENCERRADA!'

#=-=-=-=-=-=-=-=-==-=
"""
FUNÇÕES
"""

def retornar_pagina(nav): #Função do #back
  try:
    nova_pagina = nav.pop() #vai
    print(f'retornando para {nova_pagina}')
    return nova_pagina
  except AssertionError:
    print('Não há página anterior')
    return None

def navegacao(): #Esqueleto da função de navegação, ainda tá muito lisa
  nav = Navegador()

  while True:
    comando = input('Digite uma URL, #back ou #sair: ')

    if comando == '#back':
      retornar_pagina(nav)
    elif comando == '#sair':
      print(nav.encerrar())
      break
    else:
      nav.push(comando)
      print(f'Acessando: {comando}')

if __name__ == "__main__": # Pra fazer rodar
    navegacao()