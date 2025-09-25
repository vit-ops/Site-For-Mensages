from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
from datetime import datetime

app = Flask(__name__)

# Função para ler os livros do arquivo CSV
def ler_livros():
    livros = {}
    try:
        with open('livros.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                livros[row['codigo']] = {
                    'codigo': row['codigo'],
                    'titulo': row['titulo'],
                    'autor': row['autor'],
                    'emprestado': row['emprestado'] == 'True',
                    'nome': row['nome'] if row['nome'] else None,
                    'sala': row['sala'] if row['sala'] else None,
                    'data_emprestimo': row['data_emprestimo'] if row['data_emprestimo'] else None
                }
    except FileNotFoundError:
        pass
    return livros

# Função para salvar os livros no arquivo CSV
def salvar_livros(livros):
    with open('livros.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['codigo', 'titulo', 'autor', 'emprestado', 'nome', 'sala', 'data_emprestimo']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for livro in livros.values():
            writer.writerow(livro)

# Função para formatar data
def formatar_data(data_str):
    try:
        # Se vier só números: 01092025 -> 01/09/2025
        if data_str.isdigit() and len(data_str) == 8:
            return datetime.strptime(data_str, "%d%m%Y").strftime("%d/%m/%Y")
        # Se já vier com barra
        elif "/" in data_str:
            return datetime.strptime(data_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except Exception:
        return data_str
    return data_str

# Página de login
@app.route('/')
def login():
    return render_template('Login.html')

# Função de login
@app.route('/login', methods=['POST'])
def verificar_login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    
    usuarios_validos = ["victor", "mirian", "gabriela"]
    senhas_validas = ["12345678", "146533", "mirian", "142536"]
    
    if usuario.lower() in usuarios_validos and senha in senhas_validas:
        return redirect(url_for('admin'))
    else:
        return render_template('Login.html', erro="Usuário ou senha incorretos")

# Página do Admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    livros = ler_livros()
    busca = ''
    if request.method == 'POST':
        busca = request.form.get('busca', '').lower()
        if busca:
            livros = {k: v for k, v in livros.items() if 
                      busca in v['codigo'].lower() or 
                      busca in v['titulo'].lower() or 
                      busca in v['autor'].lower()}
    return render_template('Admin.html', livros=livros, busca=busca)

# Registrar livro
@app.route('/registrar', methods=['POST'])
def registrar():
    codigo = request.form['codigo']
    titulo = request.form['titulo']
    autor = request.form['autor']
    
    livros = ler_livros()
    livros[codigo] = {
        'codigo': codigo,
        'titulo': titulo,
        'autor': autor,
        'emprestado': False,
        'nome': None,
        'sala': None,
        'data_emprestimo': None
    }
    salvar_livros(livros)
    return redirect(url_for('admin'))

# Emprestar livro
@app.route('/emprestar', methods=['POST'])
def emprestar():
    data = request.get_json()
    codigo = data['codigo']
    nome = data['nome']
    sala = data['sala']
    data_emprestimo = formatar_data(data['data_emprestimo'])
    
    livros = ler_livros()
    
    if codigo in livros and not livros[codigo]['emprestado']:
        livros[codigo]['emprestado'] = True
        livros[codigo]['nome'] = nome
        livros[codigo]['sala'] = sala
        livros[codigo]['data_emprestimo'] = data_emprestimo
        salvar_livros(livros)
        return jsonify({'message': 'Livro emprestado com sucesso!'})
    else:
        return jsonify({'message': 'Erro ao emprestar o livro. Livro já emprestado ou não encontrado.'}), 400

# Devolver livro
@app.route('/devolver', methods=['POST'])
def devolver():
    data = request.get_json()
    codigo = data['codigo']
    
    livros = ler_livros()
    
    if codigo in livros and livros[codigo]['emprestado']:
        livros[codigo]['emprestado'] = False
        livros[codigo]['nome'] = None
        livros[codigo]['sala'] = None
        livros[codigo]['data_emprestimo'] = None
        salvar_livros(livros)
        return jsonify({'message': 'Livro devolvido com sucesso!'})
    else:
        return jsonify({'message': 'Erro ao devolver o livro. Livro não encontrado ou não estava emprestado.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
