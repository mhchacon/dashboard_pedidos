from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from process_planilha import processar_protheus, processar_cls
from dotenv import load_dotenv
import bcrypt
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)

# Estados do Nordeste
ESTADOS_NORDESTE = ['PE', 'PB', 'RN', 'AL', 'BA', 'MA', 'SE', 'CE']

# Configurações
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}

# Cria pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


load_dotenv()
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['dashboard_pedidos']
colecao_protheus = db['protheus']
colecao_cls = db['cls']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def root():
    return send_from_directory('../frontend', 'login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = db['usuarios'].find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'success': True, 'role': user['role']})
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

# Remover endpoint /logout
# Remover verificações de sessão nas rotas
@app.route('/dashboard')
def dashboard_page():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('../frontend', path)

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

@app.route('/dashboard_protheus')
def dashboard_protheus():
    role = request.args.get('role', '')
    uf = request.args.get('uf', '')
    doc = colecao_protheus.find_one({}, {'_id': 0})
    if not doc:
        return jsonify({'dados': [], 'ultimo_dia': '', 'valor_ultimo_dia': 0, 'ultimo_mes': '', 'valor_ultimo_mes': 0})
    dados = doc.get('tabela', [])
    if role == 'nordeste':
        dados = [d for d in dados if d.get('C5_UFDEST', '') in ESTADOS_NORDESTE]
        def soma_valor(chave):
            total = 0
            for d in dados:
                try:
                    v = float(str(d.get(chave, '0')).replace('.', '').replace(',', '.'))
                except:
                    v = 0
                total += v
            return total
        valor_ultimo_dia = soma_valor('valor_ultimo_dia')
        valor_ultimo_mes = soma_valor('total_representante')
        return jsonify({
            'dados': dados,
            'ultimo_dia': doc.get('ultimo_dia', ''),
            'valor_ultimo_dia': valor_ultimo_dia,
            'ultimo_mes': doc.get('ultimo_mes', ''),
            'valor_ultimo_mes': valor_ultimo_mes
        })
    elif role in ['admin', 'gerencia'] and uf:
        # Novo filtro: filtrar clientes pela UF
        dados_filtrados = []
        for rep in dados:
            clientes_filtrados = [cli for cli in rep.get('clientes', []) if cli.get('UF', '') == uf]
            if clientes_filtrados:
                total_rep = 0
                for cli in clientes_filtrados:
                    try:
                        v = float(str(cli.get('valor', '0')).replace('.', '').replace(',', '.'))
                    except:
                        v = 0
                    total_rep += v
                rep_novo = rep.copy()
                rep_novo['clientes'] = clientes_filtrados
                rep_novo['total_representante'] = f"{total_rep:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                dados_filtrados.append(rep_novo)
        def soma_valor_total():
            total = 0
            for d in dados_filtrados:
                try:
                    v = float(str(d.get('total_representante', '0')).replace('.', '').replace(',', '.'))
                except:
                    v = 0
                total += v
            return total
        valor_ultimo_dia = soma_valor_total()
        valor_ultimo_mes = soma_valor_total()
        return jsonify({
            'dados': dados_filtrados,
            'ultimo_dia': doc.get('ultimo_dia', ''),
            'valor_ultimo_dia': valor_ultimo_dia,
            'ultimo_mes': doc.get('ultimo_mes', ''),
            'valor_ultimo_mes': valor_ultimo_mes
        })
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

@app.route('/dashboard_cls')
def dashboard_cls():
    role = request.args.get('role', '')
    uf = request.args.get('uf', '')
    doc = colecao_cls.find_one({}, {'_id': 0})
    if not doc:
        return jsonify({'dados': [], 'ultimo_dia': '', 'valor_ultimo_dia': 0, 'ultimo_mes': '', 'valor_ultimo_mes': 0})
    dados = doc.get('tabela', [])
    if role == 'nordeste':
        dados = [d for d in dados if d.get('UF', '') in ESTADOS_NORDESTE]
        def soma_valor(chave):
            total = 0
            for d in dados:
                try:
                    v = float(str(d.get(chave, '0')).replace('.', '').replace(',', '.'))
                except:
                    v = 0
                total += v
            return total
        valor_ultimo_dia = soma_valor('valor_ultimo_dia')
        valor_ultimo_mes = soma_valor('total_representante')
        return jsonify({
            'dados': dados,
            'ultimo_dia': doc.get('ultimo_dia', ''),
            'valor_ultimo_dia': valor_ultimo_dia,
            'ultimo_mes': doc.get('ultimo_mes', ''),
            'valor_ultimo_mes': valor_ultimo_mes
        })
    elif role in ['admin', 'gerencia'] and uf:
        # Novo filtro: filtrar clientes pela UF
        dados_filtrados = []
        for rep in dados:
            clientes_filtrados = [cli for cli in rep.get('clientes', []) if cli.get('UF', '') == uf]
            if clientes_filtrados:
                total_rep = 0
                for cli in clientes_filtrados:
                    try:
                        v = float(str(cli.get('valor', '0')).replace('.', '').replace(',', '.'))
                    except:
                        v = 0
                    total_rep += v
                rep_novo = rep.copy()
                rep_novo['clientes'] = clientes_filtrados
                rep_novo['total_representante'] = f"{total_rep:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                dados_filtrados.append(rep_novo)
        def soma_valor_total():
            total = 0
            for d in dados_filtrados:
                try:
                    v = float(str(d.get('total_representante', '0')).replace('.', '').replace(',', '.'))
                except:
                    v = 0
                total += v
            return total
        valor_ultimo_dia = soma_valor_total()
        valor_ultimo_mes = soma_valor_total()
        return jsonify({
            'dados': dados_filtrados,
            'ultimo_dia': doc.get('ultimo_dia', ''),
            'valor_ultimo_dia': valor_ultimo_dia,
            'ultimo_mes': doc.get('ultimo_mes', ''),
            'valor_ultimo_mes': valor_ultimo_mes
        })
    return jsonify({
        'dados': doc.get('tabela', []),
        'ultimo_dia': doc.get('ultimo_dia', ''),
        'valor_ultimo_dia': doc.get('valor_ultimo_dia', 0),
        'ultimo_mes': doc.get('ultimo_mes', ''),
        'valor_ultimo_mes': doc.get('valor_ultimo_mes', 0)
    })

@app.route('/luzarte.ico')
def favicon():
    return send_from_directory('../frontend/static', 'luzarte.ico')

@app.route('/export_dashboard_image')
def export_dashboard_image():
    from datetime import datetime
    role = request.args.get('role', '')
    uf = request.args.get('uf', '')
    # Buscar dados do Protheus e CLS
    doc_protheus = colecao_protheus.find_one({}, {'_id': 0})
    doc_cls = colecao_cls.find_one({}, {'_id': 0})
    # Preparar dados agrupados por representante
    def agrupar_representantes(dados, uf_key=None):
        reps = []
        total_geral = 0.0
        for rep in dados:
            if role == 'nordeste' and uf_key:
                if rep.get(uf_key, '') not in ESTADOS_NORDESTE:
                    continue
            if role in ['admin', 'gerencia'] and uf and uf_key:
                if rep.get(uf_key, '') != uf:
                    continue
            nome = rep['representante']
            try:
                total = float(str(rep['total_representante']).replace('.', '').replace(',', '.'))
            except Exception:
                total = 0.0
            reps.append((nome, total))
            total_geral += total
        reps.sort(key=lambda x: x[1], reverse=True)
        return reps, total_geral
    dados_protheus = doc_protheus.get('tabela', []) if doc_protheus else []
    dados_cls = doc_cls.get('tabela', []) if doc_cls else []
    reps_aprovados, total_aprovados = agrupar_representantes(dados_protheus, uf_key='C5_UFDEST')
    reps_aprovacao, total_aprovacao = agrupar_representantes(dados_cls, uf_key='UF')
    # Cabeçalho: mês/ano e total geral em português
    hoje = datetime.now()
    meses_pt = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    mes_ano = f"{meses_pt[hoje.month-1]} {hoje.year}"
    if doc_protheus and doc_protheus.get('ultimo_mes'):
        try:
            ano, mes = doc_protheus['ultimo_mes'].split('-')
            mes_ano = f"{meses_pt[int(mes)-1]} {ano}"
        except:
            pass
    def formatar_valor(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    largura = 900
    altura = 1200 + 30 * (len(reps_aprovacao) + len(reps_aprovados))
    img = Image.new('RGB', (largura, altura), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype('arial.ttf', 32)
        font_header = ImageFont.truetype('arialbd.ttf', 22)
        font = ImageFont.truetype('arial.ttf', 20)
        font_bold = ImageFont.truetype('arialbd.ttf', 20)
        font_small = ImageFont.truetype('arial.ttf', 16)
    except:
        font_title = font_header = font = font_bold = font_small = None
    y = 30
    # Cabeçalho
    draw.text((largura//2-80, y), mes_ano, fill=(0,0,0), font=font_title)
    # Legenda 'Total Geral'
    draw.text((largura-260, y-10), 'Total Geral', fill=(80,80,80), font=font_small)
    draw.text((largura-260, y+18), formatar_valor(total_aprovacao+total_aprovados), fill=(0,0,0), font=font_title)
    y += 50
    # Em aprovação
    draw.text((30, y), 'Em aprovação', fill=(0,0,0), font=font_header)
    y += 30
    draw.rectangle([30, y, largura-30, y+32], fill=(230,230,230))
    draw.text((40, y+6), 'Representante', fill=(0,0,0), font=font_bold)
    draw.text((largura-220, y+6), 'Total', fill=(0,0,0), font=font_bold)
    y += 32
    alt = False
    for nome, total in reps_aprovacao:
        if alt:
            draw.rectangle([30, y, largura-30, y+28], fill=(245,245,245))
        draw.text((40, y+4), nome, fill=(0,0,0), font=font)
        draw.text((largura-220, y+4), formatar_valor(total), fill=(0,0,0), font=font)
        y += 28
        alt = not alt
    draw.rectangle([30, y, largura-30, y+32], fill=(230,230,230))
    draw.text((40, y+6), 'Total Geral', fill=(0,0,0), font=font_bold)
    draw.text((largura-220, y+6), formatar_valor(total_aprovacao), fill=(0,0,0), font=font_bold)
    y += 50
    # Aprovados
    draw.text((30, y), 'Aprovados', fill=(0,0,0), font=font_header)
    y += 30
    draw.rectangle([30, y, largura-30, y+32], fill=(230,230,230))
    draw.text((40, y+6), 'Representante', fill=(0,0,0), font=font_bold)
    draw.text((largura-220, y+6), 'Total', fill=(0,0,0), font=font_bold)
    y += 32
    alt = False
    for nome, total in reps_aprovados:
        if alt:
            draw.rectangle([30, y, largura-30, y+28], fill=(245,245,245))
        draw.text((40, y+4), nome, fill=(0,0,0), font=font)
        draw.text((largura-220, y+4), formatar_valor(total), fill=(0,0,0), font=font)
        y += 28
        alt = not alt
    draw.rectangle([30, y, largura-30, y+32], fill=(230,230,230))
    draw.text((40, y+6), 'Total Geral', fill=(0,0,0), font=font_bold)
    draw.text((largura-220, y+6), formatar_valor(total_aprovados), fill=(0,0,0), font=font_bold)
    y += 40
    img = img.crop((0, 0, largura, min(y+20, altura)))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(
        buf,
        mimetype='image/png',
        as_attachment=True,
        download_name='dashboard.png'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 