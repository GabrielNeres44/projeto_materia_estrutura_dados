import os
from google.colab import drive
import requests

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
DOCUMENTO NO DRIVE PRAS URL
**FALTA SÓ FAZER A VERIFICAÇÃO DAS URL**
> QUALQUER URL DIGITADA É DADA COMO VÁLIDA, TEM ALGUMA FUNÇÃO, PROVAVELMENTE,
> QUE TÁ RETORNANDO UMA STRING AO INVÉS DE BOOLEANO
"""

class Site_atual:
  def __init__(self, carga=0, prox=None):
    self.carga = carga
    self.prox = prox

  def __repr__(self):
    return '%s/%s' % (self.carga, self.prox)

class Navegador:
  def __init__(self):
    self.__topo = None #URL inicial, começa vazia, logicamente
    self.__contador = 0 #apenas simbólico pra contar qnts URL's foram acessadas

  def is_empty(self):
     return self.__topo is None

  @property
  def topo(self):
      return self.__topo

  @property
  def contador(self):
      return self.__contador

  def push(self, elemento): #vai adicionar urls no topo da
     site = Site_atual(elemento)
     site.prox = self.topo
     self.__topo = site
     self.__contador += 1

  def pop(self): #vai excluir o ultimo URL, o atual no caso.
  #Esse é o método que tem que ligar em uma função para usar o #back
    assert self.__topo != None, "Nenhuma página anterior"
    self.__topo = self.__topo.prox #transforma a URL atual na anterior a ela
    self.__contador -= 1
    if self.__topo != None:
      return self.__topo.carga
    return "Página inicial" #Se não exixtir nenhuma página antes

  def encerrar(self): #colocar esse método com a função de #sair
    return 'NAVEGAÇÃO ENCERRADA!'

"""
==================================================================================
                          GERENCIAMENTO DAS URLs
==================================================================================
"""


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
    # Certifica-se de que o diretório existe
    diretorio = os.path.dirname(nome_arquivo)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)
        print(f"Diretório '{diretorio}' criado.")

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
    Devemos verificar se a url é válida. Para isso, usaremos request
    '''
def verifica_url(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return True, None # Always return a tuple: (boolean, message or None)
    except requests.exceptions.RequestException as e:
        return False, f"Erro: {e}"

def salvar_url_no_arquivo(nome_arquivo, url):

    """
    Salva uma URL nova **apenas se ela NÃO estiver cadastrada**.
    Assim evitamos duplicação no arquivo.
    """
    '''
    verificando se a url é válida
    '''
    is_valid, _ = verifica_url(url)
    if not is_valid:
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

def limpar_arquivo(nome_arquivo):
    """
    Apaga TUDO que tem no arquivo, deixando ele vazio.
    """
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        pass  # não escreve nada = limpa
    print("Todas as URLs foram apagadas!")

def url_valida(nome_arquivo, url):
    """
    Verifica se a URL está cadastrada no arquivo.
    Retorna True (está cadastrada) ou False (não está cadastrada).
    """
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()
    if url in conteudo:
        return True
    else:
        return False

"""
==================================================================================
                        INTERFACE DO GUIZINBROWSER
==================================================================================
"""
def exibir_browser(nav):
  print('======================================')
  print('PÁGINA ATUAL:')
  if nav.topo:
    print(' ->', nav.topo.carga)
  else:
    print(' -> Página inicial')
  print('\n HISTÓRICO: ')
  temp = nav.topo
  pos = 1
  while temp:
    print(f'  {pos}. {temp.carga}')
    temp = temp.prox
    pos += 1

def retornar_pagina(nav): #Função do #back
  try:
    nova_pagina = nav.pop() #vai
    print(f'retornando para {nova_pagina}')
    return nova_pagina
  except AssertionError:
    print('Não há página anterior')
    return None

def navegacao():
  criar_arquivo_se_nao_existir(caminho)

  nav = Navegador()

  print("\n============= GUIZINBROWSER2000 ============")
  print("Comandos:")
  print(" \u2022 Digite qualquer URL válida para acessar")
  print(" \u2022 #back  \u2192 voltar para página anterior")
  print(" \u2022 #add <url> \u2192 cadastrar URL válida")
  print(" \u2022 #sair  \u2192 encerrar navegação")
  print("==============================================\n")

  while True:
      exibir_browser(nav)

      comando = input("Digite uma URL ou comando (#back, #add, #sair): ")

      if comando == "#back":

        retornar_pagina(nav)

      elif comando.startswith("#add"):

        partes = comando.split()

        if len(partes) < 2:

              print("> Uso correto: #add https://exemplo.com")

        else:
            #
            is_valid, _ = verifica_url(partes[1]) # Unpack the tuple
            if is_valid:
                salvar_url_no_arquivo(caminho, partes[1])
            else:
                print(f"> A URL '{partes[1]}' é inválida. Não foi adicionada ao histórico.")

      elif comando == "#sair":

        print(nav.encerrar())

        break

      else:

          # acessar uma URL
        is_valid, _ = verifica_url(comando)
        if is_valid:
            nav.push(comando)

            print(f"> Acessando: {comando}")

        else:

            print("> Esta URL é inválida. Não foi acessada.")

# ATIVA o navegador
navegacao()