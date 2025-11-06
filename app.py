from flask import Flask, render_template, request, redirect, url_for, flash,session
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
    conn = get_db_connection()
    categorias  = conn.execute('SELECT * FROM categorias').fetchall()
    conn.close()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        categoria = request.form['categoria']
        data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not nome:
            flash('Nome do produto é obrigatório!', 'danger')
        elif not preco:
            flash('Preço do produto é obrigatório!', 'danger')
        elif not quantidade:
            flash('Quantidade do produto é obrigatória!', 'danger')
        elif not categoria:
            flash('Categoria do produto é obrigatória','danger')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO produtos (nome, descricao, preco, quantidade, data_cadastro,Categoria) VALUES (?, ?, ?, ?, ?,?)',
                (nome, descricao, preco, quantidade, data_cadastro,categoria)
            )
            conn.commit()
            last_id = conn.cursor().lastrowid
            conn.close()
            flash(f'Produto adicionado com sucesso! ID:{last_id}', 'success')
            return redirect(url_for('index'))
    
    return render_template('adicionar_produto.html', categorias = categorias)

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


@app.route('/catalogo')
def catalogo():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    categorias  = conn.execute('SELECT * FROM categorias').fetchall()
    precoMaximo = conn.execute('SELECT MAX(preco) FROM produtos').fetchone()
    if precoMaximo and precoMaximo[0] is not None:
            # Pegamos o primeiro (e único) item da tupla, que é o nosso preço.
            maior_preco = precoMaximo[0]
    
    conn.close()
    return render_template('catalogo.html',produtos = produtos, categorias = categorias , maior_preco = maior_preco )

@app.route('/produto_cliente/<int:id>')
def visualizar_produto_cliente(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if produto is None:
        flash('Produto não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('visualizar_produto_cliente.html', produto=produto)

@app.route('/teste')
def visualizar_produto_Teste():
    return render_template('visualizar_produto_cliente.html')
@app.route('/login/' , methods = ['GET','POST'])
def login():
    if request.method  == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        conta = conn.execute('SELECT * FROM contas WHERE email = ?', (email,)).fetchone()
        conn.close()
        if not email:
            flash('O Email é obrigatório!', 'danger')
        elif not password:
            flash('Senha é obrigatório!', 'danger')
        elif conta is None:
            flash('Email ou senha incorretos')
        elif conta['password'] != password:
            flash('Email ou Senha incorretos')
        session['is_logged'] = True
        session['nickname'] = conta['nickname']
        session['is_admin'] = conta['is_admin']
        if conta['is_admin']:
            return redirect(url_for('index'))
        return redirect(url_for('catalogo'))

    return render_template('login.html')
@app.route('/register/', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        nickname = request.form['nickname']
        conn = get_db_connection()
        conta = conn.execute('SELECT * FROM contas WHERE email = ?', (email,)).fetchone()
        conn.close()
        if not email:
            flash('O Email é obrigatório!', 'danger')
        elif not password:
            flash('Senha é obrigatório!', 'danger')
        elif not password_confirm:
            flash('A confirmação da senha é obrigatória!', 'danger')
        elif password != password_confirm:
            flash('A confirmação da senha precisa ser igual a senha!', 'danger')
        elif conta is not None:
            flash('Esse Email já possui cadastro no sistema', 'danger')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO contas (email, password, nickname) VALUES (?, ?, ?)',
                (email, password,nickname)
            )
            conn.commit()
            conn.close()
            flash('Cadastro efetuado com sucesso!', 'success')
            return redirect(url_for('login'))


    return render_template('register.html')

@app.route('/logout/')
def logout():
    session.clear()

    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

# Inicializa o banco de dados e inicia a aplicação
if __name__ == '__main__':
    app.run(debug=True)