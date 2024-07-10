#Login
#Rotas / , /login, /logout , /manage_users , /home, /ssh-key/ , /webhook/

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination, get_page_args
import subprocess
import os
import random
import string


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class WebhookKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(30), nullable=False)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    readonly = db.Column(db.Boolean, default=False)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  # Novo campo
    tipo = db.Column(db.String(50), nullable=False)
    cron = db.Column(db.String(100), nullable=True)
    script = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Registro {self.id}>'    

with app.app_context():
    db.create_all()

    # Verifica se há usuários na tabela e cria um administrador padrão se não houver nenhum
    if Usuario.query.count() == 0:
        admin_user = Usuario(
            usuario='admin',
            senha=generate_password_hash('admin'),
            admin=True,
            readonly=False
            
        )
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            session['admin'] = user.admin
            session['readonly'] = user.readonly
            session['username'] = user.usuario 
            return redirect(url_for('home'))
        flash('Login ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario=session['username']
    return render_template('home.html', usuario=usuario,  admin=session.get('admin', False), )

@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'user_id' not in session or not session.get('admin', False) :
        return 'Acesso negado'

    if request.method == 'POST':
        if 'add_user' in request.form:
            usuario = request.form['usuario']
            senha = generate_password_hash(request.form['senha'])
            admin = request.form.get('admin') == '1'
            readonly = request.form.get('readonly') == '1'
            new_user = Usuario(usuario=usuario, senha=senha, admin=admin, readonly=readonly)
            if new_user.readonly == 1 :
                new_user.admin = 0
            db.session.add(new_user)
            db.session.commit()
            flash('Usuário cadastrado com sucesso.')
        elif 'edit_user' in request.form:
            user_id = request.form['user_id']
            user = Usuario.query.get(user_id)
            user.usuario = request.form['usuario']
            if request.form['senha']:
                user.senha = generate_password_hash(request.form['senha'])
            user.admin = request.form.get('admin') == '1'
            user.readonly = request.form.get('readonly') == '1'
            if user.readonly == 1 :
                user.admin = 0
            db.session.commit()
            flash('Usuário editado com sucesso.')
        elif 'delete_user' in request.form:
            user_id = request.form['user_id']
            user = Usuario.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            flash('Usuário apagado com sucesso.')
        return redirect(url_for('manage_users'))

    usuarios = Usuario.query.all()
    return render_template('manage_users.html', usuarios=usuarios)


@app.route('/jobs/')
def jobs():
    if 'user_id' not in session or session.get('readonly', True):
        return 'Acesso negado'
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search = request.args.get('search')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 10

    if search:
        registros = Registro.query.filter(Registro.nome.like(f'%{search}%')).offset(offset).limit(per_page).all()
        total = Registro.query.filter(Registro.nome.like(f'%{search}%')).count()
    else:
        registros = Registro.query.offset(offset).limit(per_page).all()
        total = Registro.query.count()
    
    pagination = Pagination(page=page, per_page=per_page, total=total, search=search, record_name='registros')

    return render_template('jobs.html', registros=registros, page=page, per_page=per_page, pagination=pagination, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        cron = request.form['cron'] 
        script = request.form['script']

        if Registro.query.filter_by(nome=nome).first():
            error = "Um registro com este nome já existe."
            return render_template('form.html', error=error, nome=nome, tipo=tipo, cron=cron, script=script)

        

        novo_registro = Registro(nome=nome, tipo=tipo, cron=cron, script=script)
        db.session.add(novo_registro)
        db.session.commit()
        subprocess.run('touch /tmp/new', shell=True )
        return redirect(url_for('jobs'))

    return render_template('form.html')
    subprocess.run('touch /tmp/new', shell=True )
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    registro = Registro.query.get_or_404(id)

    if request.method == 'POST':
        novo_nome = request.form['nome']
        if Registro.query.filter(Registro.nome == novo_nome, Registro.id != id).first():
            flash('Nome já existe. Escolha outro nome.')
        else:
            registro.nome = request.form['nome']
            registro.tipo = request.form['tipo']
            registro.cron = request.form['cron']
            registro.script = request.form['script']
            db.session.commit()
            subprocess.run('touch /tmp/new', shell=True, text=True)
            return redirect(url_for('jobs'))
     
    return render_template('edit.html', registro=registro)
   

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    registro = Registro.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    subprocess.run('touch /tmp/new', shell=True)
    return redirect(url_for('jobs'))
    
#executa scripts manualmente
#rotas /executa

@app.route('/executa/', methods=['GET', 'POST'])
def executa():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    registros = Registro.query.all()
    resultado_script = ""
    
    if request.method == 'POST':
        registro_id = request.form.get('registro_id')
        registro = Registro.query.get_or_404(registro_id)
        script_path = os.path.join('scripts', f'{registro.nome}.sh')

        if os.path.exists(script_path):
            result = subprocess.run(['bash', script_path], capture_output=True, text=True)
            resultado_script = result.stdout
        else:
            resultado_script = f'Script {script_path} não encontrado.'
    
    return render_template('executa.html', registros=registros, resultado_script=resultado_script)
    with app.app_context():
        db.create_all()
        
        # Adicionar um registro inicial se a tabela estiver vazia
        if Registro.query.count() == 0:
            novo_registro = Registro(
                nome='exemplo_script',
                tipo='cron',
                cron='* * * * *',
                script='echo "Este é um exemplo de script"'
            )
            db.session.add(novo_registro)
            db.session.commit()
#webhook key 
#rotas /webhook-key
def generate_random_key(length=30):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/webhook-key/', methods=['GET', 'POST'])
def webhook_key():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        if name:
            random_key = generate_random_key()
            new_key = WebhookKey(name=name, key=random_key)
            db.session.add(new_key)
            db.session.commit()
        return redirect(url_for('webhook_key'))

    keys = WebhookKey.query.all()
    return render_template('webhook-key.html', keys=keys)

@app.route('/webhook-delete/<int:id>')
def webhook_delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    key_to_delete = WebhookKey.query.get_or_404(id)
    db.session.delete(key_to_delete)
    db.session.commit()
    return redirect(url_for('webhook_key'))

SCRIPTS_DIR = "/usr/src/scripts/"

@app.route('/webhook/', methods=['POST'])
def webhook():
    data = request.json

    # Validar a chave de acesso
    access_key = data.get('key')
    valid_key = WebhookKey.query.filter_by(key=access_key).first()
    if not valid_key:
        return jsonify({"error": "Access Denied"}), 403

    # Obter o nome do script
    script_name = data.get('script_name')
    if not script_name:
        return jsonify({"error": "No script name provided"}), 400

    # Construir o caminho completo para o script
    script_path = os.path.join(SCRIPTS_DIR, f"{script_name}.sh")
     
    # Verificar se o script existe
    if not os.path.isfile(script_path):
        return jsonify({"error": "Script not found"}), 404

    try:
        # Executar o script e capturar a saída
        result = subprocess.run([script_path], capture_output=True, text=True, shell=True)
        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Ler e criar chave ssh para scripts que usam ssh     
# Path to the SSH public key
ssh_key_path = '/root/.ssh/id_rsa.pub'

# Function to read the public key
def read_ssh_key():
    try:
        with open(ssh_key_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "SSH key not found. Please generate a new key."

# Route to display the SSH public key
@app.route('/ssh-key/')
def ssh_key():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    key_content = read_ssh_key()
    return render_template('ssh_key.html', key_content=key_content)     
# Route to generate a new SSH key
@app.route('/generate', methods=['POST'])
def generate_key():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Remove the existing SSH key files
    os.system('rm -f /root/.ssh/id_rsa /root/.ssh/id_rsa.pub')

    # Generate a new SSH key
    subprocess.run(['ssh-keygen', '-q', '-t', 'rsa', '-N', '', '-f', '/root/.ssh/id_rsa'], check=True)

    return redirect(url_for('ssh_key'))    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
