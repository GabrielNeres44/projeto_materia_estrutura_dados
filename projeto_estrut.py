import os
from google.colab import drive
import requests
import json

"""
==================================================================================
                ESTRUTURA DE DADOS DO NAVEGADOR GUIZINBROWSER2000
==================================================================================
"""

class Site_atual:
  def __init__(self, carga=0, prox=None):
    self.carga = carga
    self.prox = prox

  def __repr__(self):
    return '%s/%s' % (self.carga, self.prox)

class Navegador:
  def __init__(self):
    self.__topo = None
    self.__contador = 0

  def is_empty(self):
     return self.__topo is None

  @property
  def topo(self):
      return self.__topo

  @property
  def contador(self):
      return self.__contador

  def push(self, elemento):
     site = Site_atual(elemento)
     site.prox = self.topo
     self.__topo = site
     self.__contador += 1

  def pop(self):
    assert self.__topo != None, "Nenhuma página anterior"
    self.__topo = self.__topo.prox
    self.__contador -= 1
    if self.__topo != None:
      return self.__topo.carga
    return "Página inicial"

  def encerrar(self):
    return 'NAVEGAÇÃO ENCERRADA!'

"""
==================================================================================
                    ESTRUTURA PARA PÁGINAS INTERNAS (ÁRVORE)
==================================================================================
"""

class NoPagina:
    """
    Representa um nó na árvore de páginas internas.
    Cada nó pode ter até 2 filhos (conforme especificação do projeto).
    """
    def __init__(self, caminho):
        self.caminho = caminho  # Ex: "/tsi", "/professores"
        self.filhos = []  # Lista de até 2 filhos

    def adicionar_filho(self, caminho):
        """Adiciona uma página interna (filho) se ainda não atingiu o limite de 2."""
        if len(self.filhos) >= 2:
            return False, "Limite de 2 páginas internas atingido"

        # Verifica se já existe
        for filho in self.filhos:
            if filho.caminho == caminho:
                return False, f"A página '{caminho}' já existe"

        novo_filho = NoPagina(caminho)
        self.filhos.append(novo_filho)
        return True, f"Página '{caminho}' adicionada com sucesso"

    def buscar_filho(self, caminho):
        """Busca um filho pelo caminho."""
        for filho in self.filhos:
            if filho.caminho == caminho:
                return filho
        return None

    def listar_filhos(self):
        """Retorna lista com os caminhos dos filhos."""
        return [filho.caminho for filho in self.filhos]


class SistemaURLs:
    """
    Gerencia todas as URLs cadastradas e suas páginas internas.
    Estrutura: dicionário onde chave = domínio raiz, valor = NoPagina (raiz da árvore)
    """
    def __init__(self, arquivo_urls):
        self.arquivo_urls = arquivo_urls
        self.urls = {}  # Dicionário: domínio -> NoPagina raiz
        self.carregar_urls()

    def extrair_dominio(self, url):
        """Extrai o domínio base de uma URL completa."""
        url_limpa = url.replace("https://", "").replace("http://", "")
        return url_limpa.split('/')[0]

    def carregar_urls(self):
        """Carrega URLs do arquivo JSON."""
        if os.path.exists(self.arquivo_urls):
            try:
                with open(self.arquivo_urls, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        dados = json.loads(conteudo)
                        # Reconstrói a estrutura
                        for dominio, estrutura in dados.items():
                            self.urls[dominio] = self._reconstruir_arvore(estrutura)
            except json.JSONDecodeError:
                print("Erro ao ler arquivo de URLs. Criando novo...")
                self.urls = {}

    def _reconstruir_arvore(self, estrutura):
        """Reconstrói a árvore a partir do dicionário salvo."""
        no = NoPagina(estrutura['caminho'])
        for filho_dict in estrutura.get('filhos', []):
            filho = self._reconstruir_arvore(filho_dict)
            no.filhos.append(filho)
        return no

    def _serializar_arvore(self, no):
        """Converte a árvore em dicionário para salvar em JSON."""
        return {
            'caminho': no.caminho,
            'filhos': [self._serializar_arvore(filho) for filho in no.filhos]
        }

    def salvar_urls(self):
        """Salva as URLs no arquivo JSON."""
        dados = {}
        for dominio, raiz in self.urls.items():
            dados[dominio] = self._serializar_arvore(raiz)

        with open(self.arquivo_urls, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def adicionar_url(self, url_completa):
        """
        Adiciona uma URL com possibilidade de páginas internas.
        Ex: www.ifpb.edu.br/tsi/professores
        """
        url_limpa = url_completa.replace("https://", "").replace("http://", "")
        partes = url_limpa.split('/')
        dominio = partes[0]

        # Se o domínio não existe, cria
        if dominio not in self.urls:
            self.urls[dominio] = NoPagina("")  # Raiz vazia
            print(f" Domínio '{dominio}' cadastrado")

        # Navega pela árvore criando os caminhos internos
        no_atual = self.urls[dominio]
        caminho_construido = ""

        for i in range(1, len(partes)):
            caminho = "/" + partes[i]
            caminho_construido += caminho

            filho = no_atual.buscar_filho(caminho)
            if not filho:
                sucesso, msg = no_atual.adicionar_filho(caminho)
                if not sucesso:
                    return False, msg
                filho = no_atual.buscar_filho(caminho)
                print(f" Página interna '{caminho_construido}' adicionada")

            no_atual = filho

        self.salvar_urls()
        return True, f"URL '{url_completa}' cadastrada com sucesso!"

    def url_valida(self, url_completa):
        """Verifica se uma URL completa é válida (existe no sistema)."""
        url_limpa = url_completa.replace("https://", "").replace("http://", "")
        partes = url_limpa.split('/')
        dominio = partes[0]

        if dominio not in self.urls:
            return False

        if len(partes) == 1:  # Só o domínio
            return True

        # Verifica se o caminho interno existe
        no_atual = self.urls[dominio]
        for i in range(1, len(partes)):
            caminho = "/" + partes[i]
            filho = no_atual.buscar_filho(caminho)
            if not filho:
                return False
            no_atual = filho

        return True

    def obter_links_internos(self, url_completa):
        """Retorna os links internos disponíveis para uma URL."""
        url_limpa = url_completa.replace("https://", "").replace("http://", "")
        partes = url_limpa.split('/')
        dominio = partes[0]

        if dominio not in self.urls:
            return []

        no_atual = self.urls[dominio]

        # Navega até o nó correspondente
        for i in range(1, len(partes)):
            caminho = "/" + partes[i]
            filho = no_atual.buscar_filho(caminho)
            if not filho:
                return []
            no_atual = filho

        return no_atual.listar_filhos()

    def listar_todas_urls(self):
        """Lista todas as URLs cadastradas em formato hierárquico."""
        if not self.urls:
            print("Nenhuma URL cadastrada.")
            return

        print("\n========= URLs CADASTRADAS =========")
        for dominio, raiz in self.urls.items():
            print(f"\n{dominio}")
            self._imprimir_arvore(raiz, "")
        print("====================================\n")

    def _imprimir_arvore(self, no, prefixo):
        """Imprime a árvore de forma hierárquica."""
        for i, filho in enumerate(no.filhos):
            eh_ultimo = i == len(no.filhos) - 1
            print(f"{prefixo}{'└──' if eh_ultimo else '├──'} {filho.caminho}")
            novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
            self._imprimir_arvore(filho, novo_prefixo)

"""
==================================================================================
                          GERENCIAMENTO DAS URLs
==================================================================================
"""

drive.mount('/content/drive')
caminho_urls = '/content/drive/MyDrive/Colab Notebooks/urls_estruturadas.json'

def criar_arquivo_se_nao_existir(nome_arquivo):
    diretorio = os.path.dirname(nome_arquivo)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)
        print(f"Diretório '{diretorio}' criado.")

    if not os.path.exists(nome_arquivo):
        print(f"Arquivo '{nome_arquivo}' não encontrado. Criando novo arquivo...")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write("{}")

def formatar_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"https://{url}"
    return url

def verifica_url(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return True, None
    except requests.exceptions.RequestException as e:
        return False, f"Erro: {e}"

def nome_do_site(dominio):
    dominio = dominio.replace("www.", "").replace("https://", "").replace("http://", "")
    return dominio.split("/")[0].split(".")[0]

# =============================================================================
#                MENSAGENS ESPECÍFICAS PARA LINKS INTERNOS (PORTAIS)
# =============================================================================

MENSAGENS_POR_CAMINHO = {
    "/tsi": "Você está na área do Curso tecnólogo em Sistemas para Internet.",
    "/tsi/professores": "Este é o portal dos professores.",
    "/tsi/alunos": "Este é o portal dos alunos.",
}

def extrair_caminho(url_completa: str) -> str:
    """
    Retorna apenas o caminho da URL.
    Ex: https://www.ifpb.edu.br/tsi/professores -> /tsi/professores
    Ex: https://www.ifpb.edu.br -> /
    """
    url_limpa = url_completa.replace("https://", "").replace("http://", "")
    partes = url_limpa.split("/", 1)
    if len(partes) == 1:
        return "/"
    caminho = "/" + partes[1].strip("/")
    return caminho if caminho else "/"

def mensagem_da_pagina(url_completa: str):
    """
    Retorna a mensagem específica para aquela página (se existir).
    Se não existir, gera uma mensagem automática:
    "Este é o portal de <ultima_parte>."
    """
    caminho = extrair_caminho(url_completa)

    # 1) Se tiver mensagem cadastrada, usa ela
    if caminho in MENSAGENS_POR_CAMINHO:
        return MENSAGENS_POR_CAMINHO[caminho]

    # 2) Fallback automático (somente para páginas internas)
    if caminho == "/" or caminho.strip("/") == "":
        return None

    ultima_parte = caminho.strip("/").split("/")[-1]
    ultima_parte = ultima_parte.replace("_", " ").replace("-", " ")
    ultima_parte = ultima_parte.lower()

    return f"Este é o portal de {ultima_parte}."

# =============================================================================
#        GERENCIAMENTO DE CONTEÚDO EM ARQUIVOS TEXTO (1 ARQUIVO POR URL)
# =============================================================================

# Pasta onde ficarão os arquivos .txt de cada URL
PASTA_CONTEUDOS = "/content/drive/MyDrive/Colab Notebooks/conteudos"

def garantir_pasta_conteudos():
    """
    Cria a pasta de conteúdos caso ela ainda não exista.
    """
    if not os.path.exists(PASTA_CONTEUDOS):
        os.makedirs(PASTA_CONTEUDOS, exist_ok=True)

def caminho_arquivo(url):
    """
    Converte a URL em um nome de arquivo válido.
    Ex:
    https://www.ifpb.edu.br/tsi  ->  www.ifpb.edu.br_tsi.txt
    """
    nome = url.replace("https://", "").replace("http://", "")
    nome = nome.replace("/", "_")
    return f"{PASTA_CONTEUDOS}/{nome}.txt"

def exibir_conteudo(url):
    """
    Exibe na tela o conteúdo do arquivo associado à URL,
    conforme exigido no enunciado do projeto.
    """
    garantir_pasta_conteudos()
    arquivo = caminho_arquivo(url)

    print(f"\nurl: {url}")

    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            print(f.read())

"""
==================================================================================
                        COMANDOS DISPONÍVEIS DO SISTEMA
==================================================================================
"""

COMANDOS = {
    "#help": "Exibe esta mensagem de ajuda com todos os comandos disponíveis.",
    "#back": "Retorna para a página anterior utilizando a pilha.",
    "#add <url>": "Cadastra uma URL com suas páginas internas no sistema.",
    "#showhist": "Exibe o histórico completo de páginas visitadas.",
    "#showurls": "Lista todas as URLs cadastradas de forma hierárquica.",
    "#sair": "Encerra a navegação e finaliza o programa."
}

def comando_help():
    print("\n=========== AJUDA DO GUIZINBROWSER2000 ===========\n")
    for comando, descricao in COMANDOS.items():
        print(f"{comando}")
        print(f"  -> {descricao}\n")
    print("Digite uma URL válida para acessar uma nova página.")
    print("URLs iniciadas por '/' acessam páginas internas do domínio atual.")
    print("=================================================\n")

"""
==================================================================================
                        INTERFACE DO GUIZINBROWSER
==================================================================================
"""

def exibir_browser(nav, sistema_urls):
    print('\n======================================')
    print('HOME:')
    if nav.topo:
        print(' ->', nav.topo.carga)
        # Mostra links disponíveis
        links = sistema_urls.obter_links_internos(nav.topo.carga)
        if links:
            print('\nLinks disponíveis:')
            for link in links:
                print(f'  {link}')
    else:
        print(' -> Página inicial')
    print('======================================')

def retornar_pagina(nav):
    try:
        nova_pagina = nav.pop()
        print(f' Retornando para: {nova_pagina}')
        return nova_pagina
    except AssertionError:
        print(' Não há página anterior')
        return None

# =============================================================================
#               URLs PADRÃO CARREGADAS AO INICIAR O SISTEMA
# =============================================================================

URLS_DEFAULT = [
    "www.ifpb.edu.br",
    "www.ifpb.edu.br/tsi",
    "www.ifpb.edu.br/tsi/professores",
    "www.ifpb.edu.br/tsi/alunos"
]

def carregar_urls_default(sistema_urls):
    """
    Cadastra URLs padrão automaticamente apenas se o sistema estiver vazio.
    Isso garante URLs iniciais sem duplicar dados em execuções futuras.
    """
    if sistema_urls.urls:
        return  # Já existem URLs cadastradas, não faz nada

    print("Carregando URLs padrão do sistema...\n")
    for url in URLS_DEFAULT:
        sistema_urls.adicionar_url(url)

def navegacao():
    criar_arquivo_se_nao_existir(caminho_urls)
    sistema_urls = SistemaURLs(caminho_urls)

    # carrega as urls default do sistema
    carregar_urls_default(sistema_urls)
    nav = Navegador()

    print("\n============= GUIZINBROWSER2000 ============")
    print("Comandos:")
    print(" • Digite qualquer URL válida para acessar")
    print(" • #help -> para ver os comandos disponíveis")
    print(" • Use '/' para acessar páginas internas")
    print("==============================================\n")

    while True:
        exibir_browser(nav, sistema_urls)

        comando = input("\nDigite uma URL ou comando: ").strip()

        if comando == "#help":
            comando_help()

        elif comando == "#back":
            retornar_pagina(nav)

        elif comando == "#showhist":
            print("\n===== HISTÓRICO COMPLETO =====")
            temp = nav.topo
            if not temp:
                print("Histórico vazio")
            else:
                # Primeiro coleta todas as URLs em uma lista
                historico = []
                while temp:
                    historico.append(temp.carga)
                    temp = temp.prox

                # Inverte a lista para mostrar da primeira à última
                historico.reverse()

                # Exibe numerado
                for i, url in enumerate(historico, 1):
                    print(f"  {i}ª página: {url}")
            print("==============================")

        elif comando == "#showurls":
            sistema_urls.listar_todas_urls()

        elif comando.startswith("#add"):
            partes = comando.split(maxsplit=1)
            if len(partes) < 2:
                print("> Uso correto: #add <url>")
                print("> Exemplo: #add www.ifpb.edu.br/tsi/professores")
            else:
                url = partes[1]
                sucesso, msg = sistema_urls.adicionar_url(url)
                print(f"> {msg}")

        elif comando == "#sair":
            print(nav.encerrar())
            break

        elif comando.startswith("/"):
            # Acesso a página interna do domínio atual
            if not nav.topo:
                print("> Erro: Não há domínio atual. Acesse um domínio primeiro.")
            else:
                url_atual = nav.topo.carga
                dominio = sistema_urls.extrair_dominio(url_atual)

                # extrai o caminho atual (ex: /tsi)
                caminho_atual = extrair_caminho(url_atual)

                # monta caminho relativo corretamente
                if caminho_atual == "/":
                    novo_caminho = comando
                else:
                    novo_caminho = caminho_atual.rstrip("/") + comando

                url_completa = f"https://{dominio}{novo_caminho}"


                if sistema_urls.url_valida(url_completa):
                    nav.push(url_completa)
                    print(f"> Acessando página interna: {url_completa}")

                    # Mensagem do portal (cadastrada ou fallback automático)
                    msg_portal = mensagem_da_pagina(url_completa)
                    if msg_portal:
                        print(f"\n{msg_portal}\n")

                    exibir_conteudo(url_completa)
                else:
                    print(f"> Página '{comando}' não encontrada no domínio '{dominio}'")

        else:
            # Acesso a URL completa
            url_formatada = formatar_url(comando)

            if sistema_urls.url_valida(url_formatada):
                nav.push(url_formatada)

                print(f"> Acessando: {url_formatada}")
                site = nome_do_site(url_formatada)
                print(f'\nBem vindo ao site {site}\n')

                # Se a URL completa for uma página interna cadastrada, mostra mensagem (ou fallback)
                msg_portal = mensagem_da_pagina(url_formatada)
                if msg_portal:
                    print(f"{msg_portal}\n")

                # Exibe o conteúdo do arquivo texto da URL
                exibir_conteudo(url_formatada)

            else:
                print(f"> URL '{url_formatada}' não está cadastrada no sistema.")
                print("> Dica: Use #add para cadastrar novas URLs")

# ATIVA o navegador
navegacao()
