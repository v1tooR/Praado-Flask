# Estrutura do Projeto CRUD com Flask e SQLite

```
projeto/
│
├── app.py                # Arquivo principal da aplicação
├── database.db           # Banco de dados SQLite (criado automaticamente)
│
└── templates/            # Diretório com os templates HTML
    ├── base.html         # Template base (layout principal)
    ├── index.html        # Página inicial - listagem de produtos
    ├── adicionar_produto.html    # Formulário para adicionar produtos
    ├── editar_produto.html       # Formulário para editar produtos
    └── visualizar_produto.html   # Página de detalhes do produto
```

## Como Executar a Aplicação

1. Certifique-se de ter o Python 3.7+ instalado
2. Instale as dependências:
   ```
   pip install flask
   ```
3. Execute o aplicativo:
   ```
   python app.py
   ```
4. Acesse a aplicação no navegador:
   ```
   http://localhost:5000
   ```

## Funcionalidades Implementadas

1. **Criar (Create)** - Adicionar novos produtos ao banco de dados
2. **Ler (Read)** - Visualizar lista de produtos e detalhes individuais
3. **Atualizar (Update)** - Editar informações de produtos existentes
4. **Excluir (Delete)** - Remover produtos do banco de dados
5. **Mensagens Flash** - Feedback para o usuário sobre as operações
6. **Interface Responsiva** - Bootstrap para melhor experiência em dispositivos móveis

## Estrutura do Banco de Dados

Tabela `produtos`:
- `id` (INTEGER): Chave primária autoincremental
- `nome` (TEXT): Nome do produto (obrigatório)
- `descricao` (TEXT): Descrição do produto (opcional)
- `preco` (REAL): Preço do produto (obrigatório)
- `quantidade` (INTEGER): Quantidade em estoque (obrigatório)
- `data_cadastro` (TEXT): Data de cadastro do produto

## Observações

- O aplicativo inicializa o banco de dados automaticamente na primeira execução
- Dados de exemplo são inseridos no banco de dados para demonstração
- O projeto usa o Bootstrap 5 para estilização
- Validações básicas são implementadas nos formulários