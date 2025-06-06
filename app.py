from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

# Configuração da aplicação Flask
app = Flask(__name__)
app.secret_key = 'praado_store'  # Necessário para usar flash messages

# Configurações do banco de dados
DATABASE = 'database.db'

# Função para obter conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
    return conn

# Rota para a página inicial - Lista todos os produtos
@app.route('/')
def index():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template('index.html', produtos=produtos)

# Rota para ver detalhes de um produto específico
@app.route('/produto/<int:id>')
def visualizar_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if produto is None:
        flash('Produto não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('visualizar_produto.html', produto=produto)

# Rota para adicionar um novo produto
@app.route('/produto/novo', methods=('GET', 'POST'))
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not nome:
            flash('Nome do produto é obrigatório!', 'danger')
        elif not preco:
            flash('Preço do produto é obrigatório!', 'danger')
        elif not quantidade:
            flash('Quantidade do produto é obrigatória!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO produtos (nome, descricao, preco, quantidade, data_cadastro) VALUES (?, ?, ?, ?, ?)',
                (nome, descricao, preco, quantidade, data_cadastro)
            )
            conn.commit()
            conn.close()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('index'))
    
    return render_template('adicionar_produto.html')

# Rota para editar um produto existente
@app.route('/produto/editar/<int:id>', methods=('GET', 'POST'))
def editar_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if produto is None:
        flash('Produto não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        
        if not nome:
            flash('Nome do produto é obrigatório!', 'danger')
        elif not preco:
            flash('Preço do produto é obrigatório!', 'danger')
        elif not quantidade:
            flash('Quantidade do produto é obrigatória!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE produtos SET nome = ?, descricao = ?, preco = ?, quantidade = ? WHERE id = ?',
                (nome, descricao, preco, quantidade, id)
            )
            conn.commit()
            conn.close()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
    
    return render_template('editar_produto.html', produto=produto)

# Rota para excluir um produto
@app.route('/produto/excluir/<int:id>', methods=('POST',))
def excluir_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    
    if produto is None:
        flash('Produto não encontrado!', 'danger')
    else:
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.commit()
        flash('Produto excluído com sucesso!', 'success')
    
    conn.close()
    return redirect(url_for('index'))

# Inicializa o banco de dados e inicia a aplicação
if __name__ == '__main__':
    app.run(debug=True)