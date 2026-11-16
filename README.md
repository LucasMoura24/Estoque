#Controle de Estoque - Oficina Reserva

Programa em Python, executado no terminal, para controlar a entrada, saída e transferência de mercadorias de uma loja de roupas.

O projeto nasceu de um problema real: a contagem e a anotação manual de entrada e saída de peças geravam divergências no estoque do meu trabalho. O programa registra cada movimentação por produto, tamanho e cor, e só permite dar saída no que realmente deu entrada.

Funcionalidades
Cadastro de produtos por referência e nome, mesmo sem peças em estoque
Entrada de peças informando tamanho, quantidade e cor (qualquer cor, digitada pelo usuário)
Saída de peças, permitida apenas para o que existe naquele produto, tamanho e cor
Visualização do estoque agrupada por produto, cor e tamanho, com totais
Transferência para outra loja ou cidade, com destino e data registrados
Histórico de transferências, das mais recentes para as mais antigas
Escolha da pasta do banco de dados na primeira execução
Padronização automática de cores e destinos (preto, Preto e PRETO viram PRETO)

#Tecnologias:
Python 3
SQLite (módulo sqlite3, já incluso no Python)
Módulos da biblioteca padrão: os, sys, json, datetime

Não é necessário instalar nenhuma dependência externa.

#Como executar:
Instale o Python 3
Baixe ou clone o repositório:
git clone [LINK DO SEU REPOSITÓRIO]
Entre na pasta do projeto e execute:
python Controle_de_Pecas.py

Na primeira execução, o programa pergunta onde guardar o banco de dados (loja.db):

Na mesma pasta do programa
Em outra pasta, digitando o caminho

A escolha é salva em um arquivo config.json, e nas próximas execuções o programa abre direto. Para trocar a pasta, feche o programa e apague o config.json.

#Como usar:
1. Cadastrar produto
2. Entrada de peças
3. Saída de peças
4. Ver estoque
5. Transferir para outra loja
6. Ver transferências
0. Sair
Opção	O que faz
1	Cadastra um produto (referência e nome)
2	Registra entrada: informa a referência e depois tamanho, quantidade e cor, quantas vezes precisar. Enter no tamanho encerra
3	Registra saída: referência, tamanho, cor e quantidade
4	Mostra o estoque atual
5	Registra a saída de peças para outra loja, guardando o destino
6	Mostra o histórico de transferências
Exemplo de estoque:
POLO 1 - Polo (total: 3)
   AZUL (total: 3)
      P: 1
      M: 2
Exemplo de transferência:
03/11/2026 14:30 | POL01 - Polo | AZUL P | 1 peça(s) -> LOJA CAMPINAS
Tamanhos aceitos

PP, 38, P, 40, M, 42, G, 44, GG, 46, 3G, 48, 4G, 50

A lista fica na variável TAMANHOS, no início do código, e pode ser editada para a nomenclatura de cada loja.

Estrutura do banco de dados
Tabela	Campos
produtos	id, referencia, nome
estoque	produto_id, tamanho, cor, qtd
transferencias	id, data, produto_id, tamanho, cor, qtd, destino

O banco é um arquivo loja.db, criado automaticamente. Bancos antigos sem a coluna cor são atualizados sozinhos na abertura do programa.

#Observações:
Não guarde o banco em pastas sincronizadas (OneDrive, Google Drive, Dropbox). A sincronização pode corromper o arquivo. O programa avisa quando detecta o OneDrive no caminho.
Cada computador tem o seu próprio banco. Use o programa em um computador só por loja, ou as contagens vão divergir.
A transferência registra apenas a saída da loja de origem. A loja de destino precisa registrar a entrada no próprio sistema.
Faça cópias de segurança do loja.db periodicamente (copiar o arquivo para um pen drive já resolve).
Melhorias futuras
- Exclusão de produtos e cancelamento de transferências
- Interface gráfica
- Geração de executável (.exe) para uso sem instalar o Python
Autor

[SEU NOME] - [LINK DO SEU GITHUB OU LINKEDIN]
