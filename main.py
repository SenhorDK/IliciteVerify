import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Palavras proibidas em vários idiomas
PALAVRAS_PROIBIDAS = [
    # Português
    "pornografia", "drogas", "crime", "terrorismo", "roubo", "assalto", "sequestro", "trafico", "contrabando",
    "narcoticos", "cocaina", "maconha", "heroina", "crack", "cartel", "quadrilha", "milicia", "homicidio", "porno", "hentai",
    # English
    "pornography", "drugs", "crime", "terrorism", "theft", "robbery", "kidnapping", "trafficking", "smuggling",
    "narcotics", "cocaine", "marijuana", "heroin", "cartel", "gang", "homicide", "murder", "assault",
    # Español
    "pornografia", "drogas", "crimen", "terrorismo", "asalto", "secuestro", "trafico", "contrabando",
    "narcoticos", "cocaina", "marihuana", "heroina", "cartel", "pandilla", "homicidio", "asesinato", "violacion"
]

# Diretórios para ignorar
DIRETORIOS_IGNORADOS = [
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "$Recycle.Bin",
    "System Volume Information",
    "AppData\\Local\\Temp"
]

def criar_relatorio(nome_arquivo="relatorio_verificacao.txt"):
    return open(nome_arquivo, "w", encoding="utf-8")

def escrever_log(arquivo, mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    arquivo.write(f"[{timestamp}] {mensagem}\n")
    arquivo.flush()

def deve_ignorar_diretorio(caminho):
    for dir_ignorado in DIRETORIOS_IGNORADOS:
        if dir_ignorado.lower() in caminho.lower():
            return True
    return False

def buscar_arquivos(caminho, arquivo_log):
    print("\n🔍 Iniciando busca de arquivos suspeitos...")
    escrever_log(arquivo_log, "Iniciando busca de arquivos suspeitos")
    encontrados = False

    for raiz, diretorios, arquivos in os.walk(caminho):
        if deve_ignorar_diretorio(raiz):
            continue

        for arquivo in arquivos:
            for palavra in PALAVRAS_PROIBIDAS:
                if palavra.lower() in arquivo.lower():
                    encontrados = True
                    caminho_completo = os.path.join(raiz, arquivo)
                    mensagem = f"Arquivo suspeito encontrado:\nLocal: {caminho_completo}\nPalavra-chave: {palavra}"
                    print(f"\n⚠️ [ALERTA] {mensagem}")
                    escrever_log(arquivo_log, mensagem)
    
    if not encontrados:
        mensagem = "Nenhum arquivo suspeito encontrado no sistema."
        print(f"\n✅ {mensagem}")
        escrever_log(arquivo_log, mensagem)

    print("\n📊 Verificação de arquivos concluída.")
    return encontrados

def buscar_historico_chrome(arquivo_log):
    print("\n🔍 Verificando histórico do Chrome...")
    escrever_log(arquivo_log, "Verificando histórico do Chrome")
    history_path = Path(os.getenv('LOCALAPPDATA')) / "Google/Chrome/User Data/Default/History"
    return buscar_historico_sqlite(history_path, "Chrome", arquivo_log)

def buscar_historico_edge(arquivo_log):
    print("\n🔍 Verificando histórico do Microsoft Edge...")
    escrever_log(arquivo_log, "Verificando histórico do Microsoft Edge")
    history_path = Path(os.getenv('LOCALAPPDATA')) / "Microsoft/Edge/User Data/Default/History"
    return buscar_historico_sqlite(history_path, "Edge", arquivo_log)

def buscar_historico_firefox(arquivo_log):
    print("\n🔍 Verificando histórico do Firefox...")
    escrever_log(arquivo_log, "Verificando histórico do Firefox")
    firefox_path = Path(os.getenv('APPDATA')) / "Mozilla/Firefox/Profiles"

    if firefox_path.exists():
        for perfil in firefox_path.glob("*.default-release"):
            history_path = perfil / "places.sqlite"
            return buscar_historico_sqlite(history_path, "Firefox", arquivo_log)
    return False

def buscar_historico_sqlite(history_path, navegador, arquivo_log):
    encontrados = False
    urls_processadas = set()
    if history_path.exists():
        temp_path = history_path.parent / f"{navegador}_history_temp"
        shutil.copy(history_path, temp_path)

        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT url, title FROM moz_places" if navegador == "Firefox" else "SELECT url, title FROM urls")
            rows = cursor.fetchall()

            for row in rows:
                url, title = row
                if url in urls_processadas:
                    continue
                
                palavras_encontradas = [palavra for palavra in PALAVRAS_PROIBIDAS 
                                       if palavra.lower() in url.lower() or palavra.lower() in title.lower()]
                
                if palavras_encontradas:
                    encontrados = True
                    urls_processadas.add(url)
                    palavras_str = ", ".join(palavras_encontradas)
                    mensagem = f"Histórico suspeito no {navegador}:\nURL: {url}\nTítulo: {title}\nPalavras-chave: {palavras_str}"
                    print(f"\n⚠️ [ALERTA] {mensagem}")
                    escrever_log(arquivo_log, mensagem)
        except Exception as e:
            mensagem = f"Erro ao analisar histórico do {navegador}: {e}"
            print(f"\n❌ {mensagem}")
            escrever_log(arquivo_log, mensagem)
        
        conn.close()
        os.remove(temp_path)

        if not encontrados:
            mensagem = f"Nenhum histórico suspeito encontrado no {navegador}."
            print(f"\n✅ {mensagem}")
            escrever_log(arquivo_log, mensagem)
    else:
        mensagem = f"{navegador} não encontrado ou histórico indisponível."
        print(f"\n⚠️ {mensagem}")
        escrever_log(arquivo_log, mensagem)
    
    return encontrados

if __name__ == "__main__":
    print("\n🔒 Iniciando verificação de segurança...\n")
    print("="*50)
    
    arquivo_log = criar_relatorio()
    escrever_log(arquivo_log, "Iniciando verificação de segurança")
    
    caminho_verificar = "C:\\Users"
    arquivos_suspeitos = buscar_arquivos(caminho_verificar, arquivo_log)
    
    print("="*50)
    chrome_suspeito = buscar_historico_chrome(arquivo_log)
    
    print("="*50)
    edge_suspeito = buscar_historico_edge(arquivo_log)
    
    print("="*50)
    firefox_suspeito = buscar_historico_firefox(arquivo_log)
    
    print("\n📊 Resumo da verificação:")
    print("="*50)
    resumo = f"""
Resumo da verificação:
- Arquivos suspeitos encontrados: {'Sim ⚠️' if arquivos_suspeitos else 'Não ✅'}
- Histórico suspeito no Chrome: {'Sim ⚠️' if chrome_suspeito else 'Não ✅'}
- Histórico suspeito no Edge: {'Sim ⚠️' if edge_suspeito else 'Não ✅'}
- Histórico suspeito no Firefox: {'Sim ⚠️' if firefox_suspeito else 'Não ✅'}"""
    print(resumo)
    escrever_log(arquivo_log, resumo)
    print("="*50)
    
    mensagem_final = "Verificação completa concluída! Um relatório detalhado foi salvo em 'relatorio_verificacao.txt'"
    print(f"\n✅ {mensagem_final}")
    escrever_log(arquivo_log, mensagem_final)
    
    arquivo_log.close()

    input("\nPressione qualquer tecla para sair...")
