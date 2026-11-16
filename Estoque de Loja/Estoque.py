import sqlite3
import os
import sys
import json
from datetime import datetime

if getattr(sys, "frozen", False):
    PASTA_PROGRAMA = os.path.dirname(sys.executable)
else:
    PASTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_CONFIG = os.path.join(PASTA_PROGRAMA, "config.json")


def escolher_pasta_banco():
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                pasta = json.load(f)["pasta_banco"]
            if os.path.isdir(pasta):
                return pasta
            print(f"A pasta salva ({pasta}) não existe mais. Escolha outra.")
        except (OSError, ValueError, KeyError):
            print("Configuração inválida. Escolha a pasta de novo.")

    while True:
        print("\nOnde guardar o banco de dados?")
        print("1. Na mesma pasta do programa")
        print("2. Em outra pasta (digitar o caminho)")
        op = input("Escolha: ").strip()

        if op == "1":
            pasta = PASTA_PROGRAMA
        elif op == "2":
            pasta = input("Caminho da pasta: ").strip().strip('"')
            if pasta == "":
                continue
        else:
            print("Digite 1 ou 2.")
            continue

        if "onedrive" in pasta.lower():
            print("Aviso: pastas do OneDrive podem corromper o banco de dados.")
            if input("Usar mesmo assim? (s/n): ").strip().lower() != "s":
                continue

        try:
            os.makedirs(pasta, exist_ok=True)
        except OSError as erro:
            print(f"Não consegui usar essa pasta: {erro}")
            continue

        try:
            with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
                json.dump({"pasta_banco": pasta}, f)
        except OSError:
            print("Não consegui salvar a escolha. Vou perguntar de novo na próxima vez.")
        return pasta


pasta_banco = escolher_pasta_banco()
conn = sqlite3.connect(os.path.join(pasta_banco, "loja.db"))
cur = conn.cursor()

TAMANHOS = ["PP", "38", "P", "40", "M", "42", "G", "44", "GG", "46", "3G", "48", "4G", "50"]


def criar_tabelas():
    cur.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, referencia TEXT UNIQUE, nome TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS estoque (produto_id INTEGER, tamanho TEXT, cor TEXT, qtd INTEGER, PRIMARY KEY (produto_id, tamanho, cor))")
    cur.execute("""CREATE TABLE IF NOT EXISTS transferencias ( id INTEGER PRIMARY KEY, data TEXT, produto_id INTEGER, tamanho TEXT, cor TEXT, qtd INTEGER, destino TEXT)""")
    cur.execute("PRAGMA table_info(estoque)")
    colunas = [c[1] for c in cur.fetchall()]
    if "cor" not in colunas:
        cur.execute("ALTER TABLE estoque RENAME TO estoque_antigo")
        cur.execute("CREATE TABLE estoque (produto_id INTEGER, tamanho TEXT, cor TEXT, qtd INTEGER, PRIMARY KEY (produto_id, tamanho, cor))")
        cur.execute("INSERT INTO estoque (produto_id, tamanho, cor, qtd) SELECT produto_id, tamanho, 'SEM COR', qtd FROM estoque_antigo")
        cur.execute("DROP TABLE estoque_antigo")
    conn.commit()


def normalizar_texto(texto):
    return " ".join(texto.split()).upper()


def normalizar_cor(cor):
    return normalizar_texto(cor)


def buscar_produto(referencia):
    cur.execute("SELECT id, nome FROM produtos WHERE referencia = ?", (referencia,))
    return cur.fetchone()


def cadastrar(referencia, nome):
    if buscar_produto(referencia):
        print("Já existe um produto com essa referência.")
        return False
    cur.execute("INSERT INTO produtos (referencia, nome) VALUES (?, ?)", (referencia, nome))
    conn.commit()
    return True


def entrada(referencia, tamanho, cor, qtd):
    produto = buscar_produto(referencia)
    if produto is None:
        print("Produto não cadastrado.")
        return False
    if tamanho not in TAMANHOS:
        print("Tamanho inválido. Use: " + ", ".join(TAMANHOS))
        return False
    if cor == "":
        print("A cor é obrigatória.")
        return False
    if qtd <= 0:
        print("A quantidade deve ser maior que zero.")
        return False
    cur.execute("""INSERT INTO estoque (produto_id, tamanho, cor, qtd) VALUES (?, ?, ?, ?) ON CONFLICT(produto_id, tamanho, cor) DO UPDATE SET qtd = qtd + excluded.qtd""", (produto[0], tamanho, cor, qtd))
    conn.commit()
    return True


def saida(referencia, tamanho, cor, qtd):
    produto = buscar_produto(referencia)
    if produto is None:
        print("Produto não cadastrado.")
        return False
    if tamanho not in TAMANHOS:
        print("Tamanho inválido. Use: " + ", ".join(TAMANHOS))
        return False
    if cor == "":
        print("A cor é obrigatória.")
        return False
    if qtd <= 0:
        print("A quantidade deve ser maior que zero.")
        return False
    cur.execute(
        "SELECT qtd FROM estoque WHERE produto_id = ? AND tamanho = ? AND cor = ?",(produto[0], tamanho, cor),)
    resultado = cur.fetchone()
    disponivel = resultado[0] if resultado else 0
    if disponivel < qtd:
        print(f"Estoque insuficiente. Disponível em {cor} tamanho {tamanho}: {disponivel}")
        return False
    cur.execute("UPDATE estoque SET qtd = qtd - ? WHERE produto_id = ? AND tamanho = ? AND cor = ?", (qtd, produto[0], tamanho, cor),)
    conn.commit()
    return True


def transferir(referencia, tamanho, cor, qtd, destino):
    produto = buscar_produto(referencia)
    if produto is None:
        print("Produto não cadastrado.")
        return False
    if tamanho not in TAMANHOS:
        print("Tamanho inválido. Use: " + ", ".join(TAMANHOS))
        return False
    if cor == "":
        print("A cor é obrigatória.")
        return False
    if destino == "":
        print("O destino é obrigatório.")
        return False
    if qtd <= 0:
        print("A quantidade deve ser maior que zero.")
        return False
    cur.execute("SELECT qtd FROM estoque WHERE produto_id = ? AND tamanho = ? AND cor = ?", (produto[0], tamanho, cor),)
    resultado = cur.fetchone()
    disponivel = resultado[0] if resultado else 0
    if disponivel < qtd:
        print(f"Estoque insuficiente. Disponível em {cor} tamanho {tamanho}: {disponivel}")
        return False

    cur.execute("UPDATE estoque SET qtd = qtd - ? WHERE produto_id = ? AND tamanho = ? AND cor = ?",(qtd, produto[0], tamanho, cor),)
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO transferencias (data, produto_id, tamanho, cor, qtd, destino) VALUES (?, ?, ?, ?, ?, ?)", (data, produto[0], tamanho, cor, qtd, destino),)
    conn.commit()
    return True


def mostrar_estoque():
    cur.execute("SELECT id, referencia, nome FROM produtos ORDER BY referencia")
    produtos = cur.fetchall()
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    print("\n--- ESTOQUE ---")
    for produto_id, referencia, nome in produtos:
        cur.execute("SELECT cor, tamanho, qtd FROM estoque WHERE produto_id = ? ORDER BY cor", (produto_id,))
        linhas = cur.fetchall()
        por_cor = {}
        for cor, tamanho, qtd in linhas:
            por_cor.setdefault(cor, {})[tamanho] = qtd

        total_produto = sum(qtd for _, _, qtd in linhas)
        print(f"\n{referencia} - {nome} (total: {total_produto})")
        if not por_cor:
            print("   sem peças")
        for cor, tamanhos in por_cor.items():
            print(f"{cor} (total: {sum(tamanhos.values())})")
            for t in TAMANHOS:
                if tamanhos.get(t, 0) > 0:
                    print(f"{t}: {tamanhos[t]}")


def mostrar_transferencias():
    cur.execute("""SELECT t.data, p.referencia, p.nome, t.tamanho, t.cor, t.qtd, t.destino FROM transferencias t JOIN produtos p ON p.id = t.produto_id ORDER BY t.id DESC""")
    linhas = cur.fetchall()
    if not linhas:
        print("Nenhuma transferência registrada.")
        return
    print("\n--- TRANSFERÊNCIAS (mais recentes primeiro) ---")
    for data, referencia, nome, tamanho, cor, qtd, destino in linhas:
        print(f"{data} | {referencia} - {nome} | {cor} {tamanho} | {qtd} peça(s) -> {destino}")


criar_tabelas()

while True:
    print("\n1. Cadastrar produto")
    print("2. Entrada de peças")
    print("3. Saída de peças")
    print("4. Ver estoque")
    print("5. Transferências e Recolhimentos")
    print("6. Ver transferências e recolhimentos")
    print("0. Sair")

    op = input("Escolha uma opção: ")

    try:
        if op == "1":
            referencia = input("Referência: ").strip().upper()
            nome = input("Nome do produto: ").strip()
            if referencia == "" or nome == "":
                print("Referência e nome são obrigatórios.")
            elif cadastrar(referencia, nome):
                print("Produto cadastrado com sucesso!")

        elif op == "2":
            referencia = input("Referência: ").strip().upper()
            produto = buscar_produto(referencia)
            if produto is None:
                print("Produto não cadastrado. Cadastre primeiro na opção 1.")
            else:
                print(f"Produto: {produto[1]}")
                print("Tamanhos: " + ", ".join(TAMANHOS))
                while True:
                    tamanho = input("Tamanho (Enter para terminar): ").strip().upper()
                    if tamanho == "":
                        break
                    qtd = int(input(f"Quantidade de {tamanho}: "))
                    cor = normalizar_cor(input(f"Cor de {tamanho}: "))
                    if entrada(referencia, tamanho, cor, qtd):
                        print("Entrada registrada!")

        elif op == "3":
            mostrar_estoque()
            referencia = input("\nReferência: ").strip().upper()
            tamanho = input("Tamanho: ").strip().upper()
            cor = normalizar_cor(input("Cor: "))
            qtd = int(input("Quantidade de saída: "))
            if saida(referencia, tamanho, cor, qtd):
                print("Saída registrada com sucesso!")

        elif op == "4":
            mostrar_estoque()

        elif op == "5":
            mostrar_estoque()
            referencia = input("\nReferência: ").strip().upper()
            tamanho = input("Tamanho: ").strip().upper()
            cor = normalizar_cor(input("Cor: "))
            qtd = int(input("Quantidade a transferir: "))
            destino = normalizar_texto(input("Destino: "))
            if transferir(referencia, tamanho, cor, qtd, destino):
                print(f"Transferência registrada! {qtd} peça(s) enviada(s) para {destino}.")

        elif op == "6":
            mostrar_transferencias()

        elif op == "0":
            break

        else:
            print("Opção inválida. Digite um número de 1 a 6 (ou 0 para sair).")

    except ValueError:
        print("Digite apenas números onde for pedido número.")
    except sqlite3.Error as erro:
        print(f"Erro no banco de dados: {erro}")

conn.close()