from flask import Flask, render_template, request, redirect, url_for, flash,session, send_from_directory, jsonify
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

def calcular_totais_carrinho():
    itens = session.get('carrinho', [])
    subtotal = sum(item.get('preco', 0) * item.get('quantidade', 0) for item in itens)
    frete = 15.00
    total = subtotal + frete
    return itens, subtotal, frete, total

def montar_resposta_carrinho(extra=None):
    itens, subtotal, frete, total = calcular_totais_carrinho()
    payload = {
        'items': itens,
        'subtotal': subtotal,
        'frete': frete,
        'total': total,
        'count': len(itens)
    }
    if extra:
        payload.update(extra)
    return payload

def solicitou_json():
    return 'application/json' in request.headers.get('Accept', '')

# Rota de listagem administrativa dos produtos
@app.route('/produtos')
def index():
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        flash('Acesso restrito aos administradores.', 'danger')
        return redirect(url_for('catalogo'))
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template('index.html', produtos=produtos)


# Rota raiz redireciona para o catálogo público
@app.route('/')
def home():
    return redirect(url_for('catalogo'))

# Rota para ver detalhes de um produto específico
@app.route('/produto/<int:id>')
def visualizar_produto(id):
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        flash('Acesso restrito aos administradores.', 'danger')
        return redirect(url_for('catalogo'))
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
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        flash('Acesso restrito aos administradores.', 'danger')
        return redirect(url_for('catalogo'))
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
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        flash('Acesso restrito aos administradores.', 'danger')
        return redirect(url_for('catalogo'))
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
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        flash('Acesso restrito aos administradores.', 'danger')
        return redirect(url_for('catalogo'))
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

@app.route('/produto_cliente/<int:id>', methods = ['GET','POST'])
def visualizar_produto_cliente(id):
    if request.method == 'POST':
        try:
            # Aqui está! Estamos pegando todos os argumentos enviados pelo formulário:

            produto_id = int(request.form.get('produto_id'))
            quantidade = int(request.form.get('quantidade', 1))
            # '1' é o valor padrão
            preco = float(request.form.get('preco'))
            nome = request.form.get('nome')
            # Obter o carrinho atual da sessão
            carrinho_atual = session.get('carrinho', [])
            imagem_url = request.form.get('image_url')
            # (A LÓGICA DE ADICIONAR/ATUALIZAR O CARRINHO QUE VIMOS ANTES)
            item_encontrado = False
            for item in carrinho_atual:
                if str(item['id']) == str(produto_id):
                    item['quantidade'] += quantidade
                    item_encontrado = True
                    break

            if not item_encontrado:
                novo_item = {
                    'id': produto_id,
                    'quantidade': quantidade,
                    'preco' : preco,
                    'nome' : nome,
                    'image_url': imagem_url

                }
                carrinho_atual.append(novo_item)

            # Salvar o carrinho atualizado de volta na sessão
            session['carrinho'] = carrinho_atual
            session.modified = True

            flash('Produto adicionado ao carrinho!', 'success')

        except Exception as e:
            flash(f'Ocorreu um erro ao adicionar o produto: {e}', 'danger')

            # Redireciona o usuário de volta para a página do carrinho
        return redirect(url_for('carrinho'))

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
        session['user_id'] = conta['id']
        session['nickname'] = conta['nickname']
        session['is_admin'] = bool(conta['is_admin'])
        session['carrinho'] = []
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
            cursor = conn.execute(
                'INSERT INTO contas (email, password, nickname) VALUES (?, ?, ?)',
                (email, password,nickname)
            )
            conn.commit()
            conta_id = cursor.lastrowid
            conta = conn.execute('SELECT * FROM contas WHERE id = ?', (conta_id,)).fetchone()
            conn.close()

            session['is_logged'] = True
            session['user_id'] = conta['id']
            session['nickname'] = conta['nickname']
            session['is_admin'] = bool(conta['is_admin'])
            session['carrinho'] = []

            flash('Cadastro efetuado com sucesso! Você já está logado.', 'success')
            if conta['is_admin']:
                return redirect(url_for('index'))
            return redirect(url_for('catalogo'))


    return render_template('register.html')

@app.route('/perfil')
def perfil():
    if not session.get('is_logged'):
        flash('Faça login para acessar o seu perfil.', 'warning')
        return redirect(url_for('login'))
    
    usuario_id = session.get('user_id')
    conn = get_db_connection()
    conta = conn.execute('SELECT * FROM contas WHERE id = ?', (usuario_id,)).fetchone()
    
    if conta is None:
        conn.close()
        session.clear()
        flash('Conta não encontrada. Faça login novamente.', 'danger')
        return redirect(url_for('login'))
    
    usuarios = []
    if conta['is_admin']:
        usuarios = conn.execute(
            'SELECT id, email, nickname, is_admin FROM contas WHERE id != ? ORDER BY nickname',
            (usuario_id,)
        ).fetchall()
    conn.close()
    
    return render_template('perfil.html', conta=conta, usuarios=usuarios)

@app.route('/perfil/alterar-senha', methods=['POST'])
def alterar_senha():
    if not session.get('is_logged'):
        flash('Faça login para alterar a senha.', 'warning')
        return redirect(url_for('login'))
    
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if not senha_atual or not nova_senha or not confirmar_senha:
        flash('Preencha todos os campos para alterar a senha.', 'danger')
        return redirect(url_for('perfil'))
    
    usuario_id = session.get('user_id')
    conn = get_db_connection()
    conta = conn.execute('SELECT * FROM contas WHERE id = ?', (usuario_id,)).fetchone()
    
    if conta is None:
        conn.close()
        session.clear()
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('login'))
    
    if senha_atual != conta['password']:
        conn.close()
        flash('A senha atual está incorreta.', 'danger')
        return redirect(url_for('perfil'))
    
    if nova_senha != confirmar_senha:
        conn.close()
        flash('A nova senha e a confirmação precisam ser iguais.', 'danger')
        return redirect(url_for('perfil'))
    
    conn.execute('UPDATE contas SET password = ? WHERE id = ?', (nova_senha, usuario_id))
    conn.commit()
    conn.close()
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('perfil'))

@app.route('/perfil/admin/<int:user_id>/toggle', methods=['POST'])
def toggle_admin(user_id):
    if not session.get('is_logged') or not bool(session.get('is_admin')):
        if solicitou_json():
            return jsonify({'success': False, 'message': 'Acesso restrito.'}), 403
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('perfil'))
    
    usuario_id = session.get('user_id')
    if user_id == usuario_id:
        if solicitou_json():
            return jsonify({'success': False, 'message': 'Você não pode alterar seu próprio status.'}), 400
        flash('Você não pode alterar seu próprio status de administrador.', 'warning')
        return redirect(url_for('perfil'))
    
    conn = get_db_connection()
    alvo = conn.execute('SELECT id, nickname, is_admin FROM contas WHERE id = ?', (user_id,)).fetchone()
    
    if alvo is None:
        conn.close()
        if solicitou_json():
            return jsonify({'success': False, 'message': 'Usuário não encontrado.'}), 404
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('perfil'))
    
    novo_status = 0 if alvo['is_admin'] else 1
    conn.execute('UPDATE contas SET is_admin = ? WHERE id = ?', (novo_status, user_id))
    conn.commit()
    conn.close()
    
    mensagem = 'perdeu o acesso de administrador.' if alvo['is_admin'] else 'agora é administrador.'
    if solicitou_json():
        return jsonify({
            'success': True,
            'target_id': user_id,
            'target_is_admin': bool(novo_status),
            'message': mensagem,
            'nickname': alvo['nickname']
        })
    flash(f"{alvo['nickname']} {mensagem}", 'success')
    return redirect(url_for('perfil'))

@app.route('/logout/')
def logout():
    session.clear()

    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/carrinho')
def carrinho():

    produtos_no_carrinho, subtotal, frete, total = calcular_totais_carrinho()

    return render_template(
        'carrinho.html',
        produtos=produtos_no_carrinho,
        subtotal=subtotal,
        frete=frete,
        total=total
    )

@app.route('/carrinho/remover/<int:produto_id>', methods=['POST'])
def remover_do_carrinho(produto_id):
    carrinho_atual = session.get('carrinho', [])
    alvo = str(produto_id)
    novo_carrinho = [item for item in carrinho_atual if str(item.get('id')) != alvo]
    removido = len(novo_carrinho) != len(carrinho_atual)

    if removido:
        session['carrinho'] = novo_carrinho
        session.modified = True

    if solicitou_json():
        status = 200 if removido else 404
        extra = {'removed_id': produto_id} if removido else {'message': 'Item não encontrado.'}
        return jsonify(montar_resposta_carrinho(extra)), status

    if not removido:
        flash('Item não foi encontrado no carrinho.', 'warning')
    else:
        flash('Item removido do carrinho!', 'info')

    return redirect(url_for('carrinho'))

@app.route('/carrinho/atualizar/<int:produto_id>', methods=['POST'])
def atualizar_carrinho(produto_id):
    nova_quantidade = request.form.get('quantidade', type=int)
    if nova_quantidade is None or nova_quantidade < 1:
        if solicitou_json():
            return jsonify({'success': False, 'message': 'Quantidade inválida.'}), 400
        flash('Informe uma quantidade válida (mínimo 1).', 'danger')
        return redirect(url_for('carrinho'))

    carrinho_atual = session.get('carrinho', [])
    alvo = str(produto_id)
    atualizado = False
    item_atualizado = None
    for item in carrinho_atual:
        if str(item.get('id')) == alvo:
            item['quantidade'] = nova_quantidade
            atualizado = True
            item_atualizado = item
            break

    if atualizado:
        session['carrinho'] = carrinho_atual
        session.modified = True
        extra = {'updated_item': item_atualizado}
        if solicitou_json():
            return jsonify(montar_resposta_carrinho(extra))
        return redirect(url_for('carrinho'))
    else:
        if solicitou_json():
            return jsonify({'success': False, 'message': 'Item não encontrado.'}), 404
        flash('Item não foi encontrado no carrinho.', 'warning')
        return redirect(url_for('carrinho'))

# Rota para servir arquivos da pasta media
@app.route('/media/<path:filename>')
def media_files(filename):
    return send_from_directory('media', filename)

# Inicializa o banco de dados e inicia a aplicação
if __name__ == '__main__':
    app.run(debug=True)
