import os
from google.colab import drive
from urllib.parse import urlparse

"""
==================================================================================
                ESTRUTURA DE DADOS DO NAVEGADOR GUIZINBROWSER2000
==================================================================================
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
==================================================================================
                              FUNÇÕES DO BROWSER
==================================================================================
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


#-=-=-==-=-=-===-=-=-=-=-=-=-===-=-=-


# =============== 1. MONTAR O GOOGLE DRIVE ====================
drive.mount('/content/drive')

# Caminho do arquivo onde as URLs serão armazenadas
caminho = '/content/drive/MyDrive/Colab Notebooks/urls.txt'


# =============== 2. CRIAR ARQUIVO SE NÃO EXISTIR ================
def criar_arquivo_se_nao_existir(nome_arquivo):
    """
    Verifica se o arquivo existe.
    Se não existir, cria um arquivo vazio.
    """
    if not os.path.exists(nome_arquivo):
        print(f"Arquivo '{nome_arquivo}' não encontrado. Criando novo arquivo...")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            pass  # cria um arquivo vazio


# =============== 3. VERIFICAR SE A URL JÁ FOI SALVA ================
def url_ja_existe(nome_arquivo, url):
    """
    Lê o arquivo e verifica se a URL já está cadastrada.
    Retorna True (existe) ou False (não existe).
    """
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return url + "\n" in f.readlines()  # evita erro com palavras parecidas


# =============== 4. SALVAR NOVA URL ==============================
'''
    Devemos verificar se a url é válida. Para isso, usaremos a biblioteca urllib
    '''
def verifica_url(url):
  try:
    resultado = urlparse(url)
    if resultado.scheme and resultado.netloc:
        return 'Url válida...'
    else:
        return 'Url inválida.'

  except:
    return 'Url inválida.'

def salvar_url_no_arquivo(nome_arquivo, url):

    '''
    verificando se a url é válida
    '''
    verificacao = verifica_url(url)
    print(verificacao)

    """
    Salva uma URL nova **apenas se ela NÃO estiver cadastrada**.
    Assim evitamos duplicação no arquivo.
    """
    if verificacao == 'Url inválida.':
      print('Url não será salva...')

    elif not url_ja_existe(nome_arquivo, url):
        with open(nome_arquivo, "a", encoding="utf-8") as f:
            f.write(url + "\n")
        print(f"URL adicionada: {url}")

    else:
        print(f"A URL '{url}' já está cadastrada! ")



# =============== 5. EXIBIR TODAS AS URLs =========================
def mostrar_urls(nome_arquivo):
    """
    Exibe todas as URLs cadastradas no arquivo.
    """
    print("\n========= URLs CADASTRADAS =========")
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()
        if conteudo.strip() == "":
            print("Nenhuma URL cadastrada ainda.")
        else:
            print(conteudo)
    print("====================================\n")


# ===== EXECUÇÃO DO PROGRAMA (TESTE SIMPLES) =====

criar_arquivo_se_nao_existir(caminho)

salvar_url_no_arquivo(caminho, "https://www.google.com")
salvar_url_no_arquivo(caminho, "https://www.openai.com")
salvar_url_no_arquivo(caminho, "https://www.google.com")  # Teste de duplicação
salvar_url_no_arquivo(caminho, "www.google.com")
salvar_url_no_arquivo(caminho, "https:/.com")


mostrar_urls(caminho)

def limpar_arquivo(nome_arquivo):
    """
    Apaga TUDO que tem no arquivo, deixando ele vazio.
    """
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        pass  # não escreve nada = limpa
    print("Todas as URLs foram apagadas!")

# USO:
limpar_arquivo(caminho)

