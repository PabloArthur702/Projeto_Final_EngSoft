from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os

# Configuração do app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'seu_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Instanciando bibliotecas
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, nullable=True)  # Torna o campo user_id opcional

# Rotas de páginas HTML
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id  # Armazena o ID do usuário na sessão
            return redirect(url_for('tasks_page'))
        else:
            return render_template('login.html', error='Credenciais inválidas.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Usuário já existe.')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/tasks')
def tasks_page():
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        return redirect(url_for('login_page'))
    return render_template('tasks.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    return redirect(url_for('login_page'))

# Rotas da API
@app.route('/tasks/api', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  # Agora retorna todas as tarefas sem filtro de usuário
    task_list = [{'id': t.id, 'title': t.title, 'done': t.done} for t in tasks]
    return jsonify(task_list)

@app.route('/tasks/api', methods=['POST'])
def create_task():
    if 'user_id' not in session:  # Verifica se o usuário está autenticado
        return jsonify({'msg': 'Usuário não autenticado.'}), 401
    
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'msg': 'O título da tarefa é obrigatório.'}), 400
    
    user_id = session['user_id']  # Obtém o ID do usuário da sessão
    new_task = Task(title=data['title'], user_id=user_id)  # Associa o user_id à tarefa
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'msg': 'Tarefa criada com sucesso!'})

@app.route('/tasks/api/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({'msg': 'Tarefa não encontrada.'}), 404
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.done = data.get('done', task.done)
    db.session.commit()
    return jsonify({'msg': 'Tarefa atualizada com sucesso!'})

@app.route('/tasks/api/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({'msg': 'Tarefa não encontrada.'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'msg': 'Tarefa excluída com sucesso!'})

# Inicialização do banco de dados
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
