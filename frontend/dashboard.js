const dashboardContainer = document.getElementById('dashboard-container');
const adminActions = document.getElementById('admin-actions');
const uploadForm = document.getElementById('upload-form');
const uploadMessage = document.getElementById('upload-message');
const dashboardDiv = document.getElementById('dashboard');
const logoutBtn = document.getElementById('logout-btn');
const uploadClsForm = document.getElementById('upload-cls-form');
const uploadClsMessage = document.getElementById('upload-cls-message');
const dashboardClsDiv = document.getElementById('dashboard-cls');
const downloadBtn = document.getElementById('download-dashboard-btn');

const API_URL = "";

let userRole = null;
let resumoProtheus = null;
let resumoCls = null;

if (uploadForm) {
    uploadForm.onsubmit = async (e) => {
        e.preventDefault();
        uploadMessage.textContent = '';
        const fileInput = document.getElementById('protheus-file');
        if (!fileInput.files.length) {
            uploadMessage.textContent = 'Selecione um arquivo XLSX.';
            return;
        }
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        const res = await fetch(`${API_URL}/upload_protheus`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            uploadMessage.textContent = 'Upload e processamento concluídos!';
            loadDashboard();
        } else {
            uploadMessage.textContent = data.message || 'Erro no upload.';
        }
    };
}

if (uploadClsForm) {
    uploadClsForm.onsubmit = async (e) => {
        e.preventDefault();
        uploadClsMessage.textContent = '';
        const fileInput = document.getElementById('cls-file');
        if (!fileInput.files.length) {
            uploadClsMessage.textContent = 'Selecione um arquivo XLSX.';
            return;
        }
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        const res = await fetch(`${API_URL}/upload_cls`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            uploadClsMessage.textContent = 'Upload e processamento da CLS concluídos!';
            loadDashboardCls();
        } else {
            uploadClsMessage.textContent = data.message || 'Erro no upload da CLS.';
        }
    };
}

logoutBtn.onclick = () => {
    localStorage.removeItem('role');
    dashboardDiv.innerHTML = '';
    dashboardClsDiv.innerHTML = '';
    dashboardContainer.style.display = 'none';
    window.location.href = 'login.html';
};

function formatarDataBR(data, tipo) {
    if (!data || data.length < 7) return data || '-';
    // Para datas no formato '2025-07-17'
    if (data.length === 10 && data.includes('-')) {
        const [ano, mes, dia] = data.split('-');
        return `${dia}/${mes}/${ano}`;
    }
    // Para datas no formato '2025-07' (mês)
    if (data.length === 7 && data.includes('-')) {
        const [ano, mes] = data.split('-');
        return `${mes}/${ano}`;
    }
    return data;
}

function renderResumoTopo() {
    const container = document.getElementById('dashboard-resumo');
    if (!resumoProtheus && !resumoCls) {
        container.innerHTML = '';
        return;
    }
    let html = '<div class="resumo-cards-topo">';
    if (resumoProtheus) {
        html += `<div class="resumo-card resumo-aprovados"><div class="resumo-label">Aprovados - Último Dia</div><div class="resumo-valor">R$ ${resumoProtheus.valor_ultimo_dia.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${formatarDataBR(resumoProtheus.ultimo_dia) || '-'}</div></div>`;
        html += `<div class="resumo-card resumo-aprovados"><div class="resumo-label">Aprovados - Último Mês</div><div class="resumo-valor">R$ ${resumoProtheus.valor_ultimo_mes.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${formatarDataBR(resumoProtheus.ultimo_mes, 'mes') || '-'}</div></div>`;
    }
    if (resumoCls) {
        html += `<div class="resumo-card resumo-aprovacao"><div class="resumo-label">Em Aprovação - Último Dia</div><div class="resumo-valor">R$ ${resumoCls.valor_ultimo_dia.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${formatarDataBR(resumoCls.ultimo_dia) || '-'}</div></div>`;
        html += `<div class="resumo-card resumo-aprovacao"><div class="resumo-label">Em Aprovação - Último Mês</div><div class="resumo-valor">R$ ${resumoCls.valor_ultimo_mes.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${formatarDataBR(resumoCls.ultimo_mes, 'mes') || '-'}</div></div>`;
    }
    html += '</div>';
    container.innerHTML = html;
}

function parseValorBR(valor) {
    if (typeof valor === 'number') return valor;
    return parseFloat(valor.replace(/\./g, '').replace(',', '.'));
}

function renderDashboard(data, container, section) {
    if (!data || !data.length) {
        container.innerHTML = '<p>Nenhum dado disponível.</p>';
        return;
    }
    // Ordenar do maior para o menor total
    data = data.slice().sort((a, b) => parseValorBR(b.total_representante) - parseValorBR(a.total_representante));
    let totalGeral = 0;
    let html = '<table class="dashboard-table"><thead><tr><th>VENDEDOR</th><th>VALOR</th></tr></thead><tbody>';
    data.forEach((rep, idx) => {
        totalGeral += parseValorBR(rep.total_representante);
        const repId = `${section}-rep-${idx}`;
        html += `<tr class="rep-header" onclick="toggleRep('${repId}')">
            <td><span class="rep-name">${rep.representante}</span> <span class="rep-toggle" id="${repId}-toggle">&#9654;</span></td>
            <td class="rep-total">R$ ${rep.total_representante}</td>
        </tr>`;
        html += `<tr class="rep-clientes-row" id="${repId}" style="display:none;"><td colspan="2"><table class="clientes-table"><thead><tr><th>CLIENTES</th><th>VALOR</th></tr></thead><tbody>`;
        html += rep.clientes.map(cli => `<tr><td>${cli.cliente}</td><td>R$ ${cli.valor}</td></tr>`).join('');
        html += `<tr class="soma-row"><td>Total do Representante</td><td>R$ ${rep.total_representante}</td></tr>`;
        html += '</tbody></table></td></tr>';
    });
    // Formatar o total geral para BR
    const totalGeralFormatado = totalGeral.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
    html += `<tr class="total-geral"><td>Total Geral</td><td><b>R$ ${totalGeralFormatado}</b></td></tr>`;
    html += '</tbody></table>';
    container.innerHTML = html;
}

window.toggleRep = function(repId) {
    const el = document.getElementById(repId);
    const toggle = document.getElementById(repId + '-toggle');
    if (el.style.display === 'none') {
        el.style.display = '';
        if (toggle) toggle.innerHTML = '&#9660;';
    } else {
        el.style.display = 'none';
        if (toggle) toggle.innerHTML = '&#9654;';
    }
};

const estadosBrasil = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
];

function criarDropdownUF() {
    const role = localStorage.getItem('role');
    if (role !== 'admin' && role !== 'gerencia') return;
    let container = document.getElementById('uf-filter-row');
    if (!container) {
        // Cria uma linha flexível para filtro e botão
        container = document.createElement('div');
        container.id = 'uf-filter-row';
        container.className = 'uf-filter-row';
        // Insere logo após o dashboard-resumo
        const resumo = document.getElementById('dashboard-resumo');
        resumo.parentNode.insertBefore(container, resumo.nextSibling);
    }
    let html = `<div class="uf-filter-group">
        <label for="uf-select" class="uf-label">UF:</label>
        <select id="uf-select" class="uf-select">
            <option value="">Todos</option>`;
    estadosBrasil.forEach(uf => {
        html += `<option value="${uf}">${uf}</option>`;
    });
    html += `</select></div>`;
    // Botão de download ao lado
    html += `<button id="download-dashboard-btn" class="download-btn-small"><span class="icon">💾</span> Baixar imagem</button>`;
    container.innerHTML = html;
    document.getElementById('uf-select').onchange = function() {
        loadDashboard();
        loadDashboardCls();
    };
    document.getElementById('download-dashboard-btn').onclick = downloadBtn.onclick;
}

async function loadDashboard() {
    dashboardDiv.innerHTML = '<em>Carregando dados...</em>';
    const role = localStorage.getItem('role');
    let url = `${API_URL}/dashboard_protheus`;
    if (role === 'nordeste') {
        url += '?role=nordeste';
    } else if ((role === 'admin' || role === 'gerencia')) {
        const uf = document.getElementById('uf-select')?.value;
        if (uf) {
            url += `?role=${role}&uf=${uf}`;
        } else {
            url += `?role=${role}`;
        }
    }
    const res = await fetch(url);
    if (res.status === 401) {
        window.location.href = 'login.html';
        return;
    }
    const data = await res.json();
    resumoProtheus = data;
    renderResumoTopo();
    renderDashboard(data.dados, dashboardDiv, 'aprovados');
}

async function loadDashboardCls() {
    dashboardClsDiv.innerHTML = '<em>Carregando dados da CLS...</em>';
    const role = localStorage.getItem('role');
    let url = `${API_URL}/dashboard_cls`;
    if (role === 'nordeste') {
        url += '?role=nordeste';
    } else if ((role === 'admin' || role === 'gerencia')) {
        const uf = document.getElementById('uf-select')?.value;
        if (uf) {
            url += `?role=${role}&uf=${uf}`;
        } else {
            url += `?role=${role}`;
        }
    }
    const res = await fetch(url);
    if (res.status === 401) {
        window.location.href = 'login.html';
        return;
    }
    const data = await res.json();
    resumoCls = data;
    renderResumoTopo();
    renderDashboard(data.dados, dashboardClsDiv, 'aprovacao');
}

// Função para expandir todos os representantes
function expandirTodosReps() {
    document.querySelectorAll('.rep-clientes-row').forEach(el => {
        el.style.display = '';
    });
    document.querySelectorAll('.rep-toggle').forEach(toggle => {
        toggle.innerHTML = '&#9660;';
    });
}

downloadBtn.onclick = function() {
    // Baixar imagem gerada pelo backend
    const role = localStorage.getItem('role');
    let url = '/export_dashboard_image';
    if (role === 'nordeste') {
        url += '?role=nordeste';
    } else if ((role === 'admin' || role === 'gerencia')) {
        const uf = document.getElementById('uf-select')?.value;
        if (uf) {
            url += `?role=${role}&uf=${uf}`;
        } else {
            url += `?role=${role}`;
        }
    }
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'dashboard.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        });
};

window.onload = () => {
    // Exibe upload só para admin
    const role = localStorage.getItem('role');
    if (role === 'admin') {
        document.getElementById('admin-actions').style.display = 'block';
    } else {
        document.getElementById('admin-actions').style.display = 'none';
    }
    // Remove botão antigo se existir
    const btnAntigo = document.getElementById('download-dashboard-btn');
    if (btnAntigo) btnAntigo.style.display = 'none';
    criarDropdownUF();
    loadDashboard();
    loadDashboardCls();
}; 