from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from process_planilha import processar_protheus, processar_cls
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Configurações
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}

# Cria pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Usuários de exemplo (em produção, use hash/senha segura e banco)
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'gerencia': {'password': 'gerencia123', 'role': 'gerencia'}
}

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['dashboard_pedidos']
colecao_protheus = db['protheus']
colecao_cls = db['cls']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('../frontend', path)

@app.route('/')
def root():
    return send_from_directory('../frontend', 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = USERS.get(username)
    if user and user['password'] == password:
        return jsonify({'success': True, 'role': user['role']})
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

@app.route('/upload_protheus', methods=['POST'])
def upload_protheus():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nome de arquivo vazio'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Processar planilha
        resultado = processar_protheus(filepath)
        colecao_protheus.delete_many({})
        colecao_protheus.insert_one(resultado)
        return jsonify({'success': True, 'message': 'Arquivo processado e dados salvos', 'filename': filename})
    return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'}), 400

@app.route('/dashboard_protheus', methods=['GET'])
def dashboard_protheus():
    doc = colecao_protheus.find_one({}, {'_id': 0})
    if not doc:
        return jsonify({'dados': [], 'ultimo_dia': '', 'valor_ultimo_dia': 0, 'ultimo_mes': '', 'valor_ultimo_mes': 0})
    return jsonify({
        'dados': doc.get('tabela', []),
        'ultimo_dia': doc.get('ultimo_dia', ''),
        'valor_ultimo_dia': doc.get('valor_ultimo_dia', 0),
        'ultimo_mes': doc.get('ultimo_mes', ''),
        'valor_ultimo_mes': doc.get('valor_ultimo_mes', 0)
    })

@app.route('/upload_cls', methods=['POST'])
def upload_cls():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nome de arquivo vazio'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Processar planilha CLS
        resultado = processar_cls(filepath)
        colecao_cls.delete_many({})
        colecao_cls.insert_one(resultado)
        return jsonify({'success': True, 'message': 'Arquivo CLS processado e dados salvos', 'filename': filename})
    return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'}), 400

@app.route('/dashboard_cls', methods=['GET'])
def dashboard_cls():
    doc = colecao_cls.find_one({}, {'_id': 0})
    if not doc:
        return jsonify({'dados': [], 'ultimo_dia': '', 'valor_ultimo_dia': 0, 'ultimo_mes': '', 'valor_ultimo_mes': 0})
    return jsonify({
        'dados': doc.get('tabela', []),
        'ultimo_dia': doc.get('ultimo_dia', ''),
        'valor_ultimo_dia': doc.get('valor_ultimo_dia', 0),
        'ultimo_mes': doc.get('ultimo_mes', ''),
        'valor_ultimo_mes': doc.get('valor_ultimo_mes', 0)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 