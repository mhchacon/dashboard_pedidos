import openpyxl
from collections import defaultdict
from datetime import datetime

def processar_protheus(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    
    # Encontrar os índices das colunas relevantes
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    idx_nome = headers.index('A3_NOME')
    idx_cliente = headers.index('C5_XNOME')
    idx_valor = headers.index('C6_VALOR')
    idx_condpag = headers.index('C5_CONDPAG')
    idx_xopfat = headers.index('C5_XOPFAT')
    idx_emissao = headers.index('C5_EMISSAO')

    dados = defaultdict(lambda: defaultdict(float))
    soma_representante = defaultdict(float)
    valores_por_dia = defaultdict(float)
    valores_por_mes = defaultdict(float)
    datas = set()

    for row in ws.iter_rows(min_row=2):
        nome = row[idx_nome].value
        cliente = row[idx_cliente].value
        valor = row[idx_valor].value
        condpag = str(row[idx_condpag].value) if row[idx_condpag].value is not None else ''
        xopfat = str(row[idx_xopfat].value) if row[idx_xopfat].value is not None else ''
        data_emissao = row[idx_emissao].value
        # Filtros
        if condpag == '103':
            continue
        if xopfat not in ('1', ''):
            continue
        if not nome or not cliente or valor is None or not data_emissao:
            continue
        # Converter valor decimal de ponto para vírgula e somar
        try:
            valor_float = float(str(valor).replace(',', '').replace('.', '.'))
        except Exception:
            continue
        # Converter data para datetime
        try:
            data_str = str(data_emissao)
            if len(data_str) == 8:
                data_dt = datetime.strptime(data_str, '%Y%m%d')
            else:
                continue
        except Exception:
            continue
        dia = data_dt.strftime('%Y-%m-%d')
        mes = data_dt.strftime('%Y-%m')
        datas.add(data_dt)
        valores_por_dia[dia] += valor_float
        valores_por_mes[mes] += valor_float
        dados[nome][cliente] += valor_float
        soma_representante[nome] += valor_float

    # Montar estrutura para dashboard
    resultado = []
    for representante, clientes in dados.items():
        clientes_list = [
            {'cliente': c, 'valor': round(v, 2)} for c, v in clientes.items()
        ]
        resultado.append({
            'representante': representante,
            'total_representante': round(soma_representante[representante], 2),
            'clientes': clientes_list
        })
    # Calcular último dia e mês
    if datas:
        ultimo_dia = max(datas)
        ultimo_dia_str = ultimo_dia.strftime('%Y-%m-%d')
        ultimo_mes = ultimo_dia.strftime('%Y-%m')
        valor_ultimo_dia = round(valores_por_dia[ultimo_dia_str], 2)
        valor_ultimo_mes = round(valores_por_mes[ultimo_mes], 2)
    else:
        valor_ultimo_dia = 0
        valor_ultimo_mes = 0
        ultimo_dia_str = ''
        ultimo_mes = ''
    return {
        'tabela': resultado,
        'ultimo_dia': ultimo_dia_str,
        'valor_ultimo_dia': valor_ultimo_dia,
        'ultimo_mes': ultimo_mes,
        'valor_ultimo_mes': valor_ultimo_mes
    }

def processar_cls(filepath):
    import openpyxl
    from collections import defaultdict
    from datetime import datetime
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    idx_status = headers.index('Status Mov.')
    idx_favoravel = headers.index('Favorável') if 'Favorável' in headers else None
    idx_representante = headers.index('Representante')
    idx_cliente = headers.index('Nome Cliente')
    idx_valor = headers.index('Valor Líquido')
    idx_emissao = headers.index('Data Emissão')

    dados = defaultdict(lambda: defaultdict(float))
    soma_representante = defaultdict(float)
    valores_por_dia = defaultdict(float)
    valores_por_mes = defaultdict(float)
    datas = set()

    for row in ws.iter_rows(min_row=2):
        status = row[idx_status].value
        favoravel = row[idx_favoravel].value if idx_favoravel is not None else 'Sim'
        representante = row[idx_representante].value
        cliente = row[idx_cliente].value
        valor = row[idx_valor].value
        data_emissao = row[idx_emissao].value
        if status not in ['Aprovação Comercial', 'Aprovação de Crédito']:
            continue
        if favoravel not in ['Sim', 'S', 'Favorável', True, 1]:
            continue
        if not representante or not cliente or valor is None or not data_emissao:
            continue
        try:
            valor_float = float(str(valor).replace(',', '').replace('.', '.'))
        except Exception:
            continue
        # Converter data para datetime
        try:
            data_dt = datetime.strptime(str(data_emissao), '%d-%m-%Y')
        except Exception:
            continue
        dia = data_dt.strftime('%Y-%m-%d')
        mes = data_dt.strftime('%Y-%m')
        datas.add(data_dt)
        valores_por_dia[dia] += valor_float
        valores_por_mes[mes] += valor_float
        dados[representante][cliente] += valor_float
        soma_representante[representante] += valor_float

    resultado = []
    for representante, clientes in dados.items():
        clientes_list = [
            {'cliente': c, 'valor': round(v, 2)} for c, v in clientes.items()
        ]
        resultado.append({
            'representante': representante,
            'total_representante': round(soma_representante[representante], 2),
            'clientes': clientes_list
        })
    # Calcular último dia e mês
    if datas:
        ultimo_dia = max(datas)
        ultimo_dia_str = ultimo_dia.strftime('%Y-%m-%d')
        ultimo_mes = ultimo_dia.strftime('%Y-%m')
        valor_ultimo_dia = round(valores_por_dia[ultimo_dia_str], 2)
        valor_ultimo_mes = round(valores_por_mes[ultimo_mes], 2)
    else:
        valor_ultimo_dia = 0
        valor_ultimo_mes = 0
        ultimo_dia_str = ''
        ultimo_mes = ''
    return {
        'tabela': resultado,
        'ultimo_dia': ultimo_dia_str,
        'valor_ultimo_dia': valor_ultimo_dia,
        'ultimo_mes': ultimo_mes,
        'valor_ultimo_mes': valor_ultimo_mes
    } 