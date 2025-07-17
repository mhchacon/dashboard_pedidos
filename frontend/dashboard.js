const loginForm = document.getElementById('login-form');
const loginContainer = document.getElementById('login-container');
const dashboardContainer = document.getElementById('dashboard-container');
const adminActions = document.getElementById('admin-actions');
const uploadForm = document.getElementById('upload-form');
const uploadMessage = document.getElementById('upload-message');
const dashboardDiv = document.getElementById('dashboard');
const logoutBtn = document.getElementById('logout-btn');
const loginError = document.getElementById('login-error');
const uploadClsForm = document.getElementById('upload-cls-form');
const uploadClsMessage = document.getElementById('upload-cls-message');
const dashboardClsDiv = document.getElementById('dashboard-cls');

let userRole = null;
let resumoProtheus = null;
let resumoCls = null;

loginForm.onsubmit = async (e) => {
    e.preventDefault();
    loginError.textContent = '';
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.success) {
        userRole = data.role;
        loginContainer.style.display = 'none';
        dashboardContainer.style.display = 'block';
        if (userRole === 'admin') {
            adminActions.style.display = 'block';
        } else {
            adminActions.style.display = 'none';
        }
        loadDashboard();
        loadDashboardCls();
    } else {
        loginError.textContent = data.message || 'Erro no login';
    }
};

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
        const res = await fetch('http://localhost:5000/upload_protheus', {
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
        const res = await fetch('http://localhost:5000/upload_cls', {
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
    userRole = null;
    dashboardDiv.innerHTML = '';
    dashboardClsDiv.innerHTML = '';
    dashboardContainer.style.display = 'none';
    loginContainer.style.display = 'block';
    loginForm.reset();
};

function renderResumoTopo() {
    const container = document.getElementById('dashboard-resumo');
    if (!resumoProtheus && !resumoCls) {
        container.innerHTML = '';
        return;
    }
    let html = '<div class="resumo-cards-topo">';
    if (resumoProtheus) {
        html += `<div class="resumo-card resumo-aprovados"><div class="resumo-label">Aprovados - Último Dia</div><div class="resumo-valor">R$ ${resumoProtheus.valor_ultimo_dia.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${resumoProtheus.ultimo_dia || '-'}</div></div>`;
        html += `<div class="resumo-card resumo-aprovados"><div class="resumo-label">Aprovados - Último Mês</div><div class="resumo-valor">R$ ${resumoProtheus.valor_ultimo_mes.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${resumoProtheus.ultimo_mes || '-'}</div></div>`;
    }
    if (resumoCls) {
        html += `<div class="resumo-card resumo-aprovacao"><div class="resumo-label">Em Aprovação - Último Dia</div><div class="resumo-valor">R$ ${resumoCls.valor_ultimo_dia.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${resumoCls.ultimo_dia || '-'}</div></div>`;
        html += `<div class="resumo-card resumo-aprovacao"><div class="resumo-label">Em Aprovação - Último Mês</div><div class="resumo-valor">R$ ${resumoCls.valor_ultimo_mes.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div><div class="resumo-data">${resumoCls.ultimo_mes || '-'}</div></div>`;
    }
    html += '</div>';
    container.innerHTML = html;
}

function renderDashboard(data, container, section) {
    if (!data || !data.length) {
        container.innerHTML = '<p>Nenhum dado disponível.</p>';
        return;
    }
    // Ordenar do maior para o menor total
    data = data.slice().sort((a, b) => b.total_representante - a.total_representante);
    let totalGeral = 0;
    let html = '<table class="dashboard-table"><thead><tr><th>VENDEDOR</th><th>VALOR</th></tr></thead><tbody>';
    data.forEach((rep, idx) => {
        totalGeral += rep.total_representante;
        const repId = `${section}-rep-${idx}`;
        html += `<tr class="rep-header" onclick="toggleRep('${repId}')">
            <td><span class="rep-name">${rep.representante}</span> <span class="rep-toggle" id="${repId}-toggle">&#9654;</span></td>
            <td class="rep-total">R$ ${rep.total_representante.toLocaleString('pt-BR', {minimumFractionDigits:2})}</td>
        </tr>`;
        html += `<tr class="rep-clientes-row" id="${repId}" style="display:none;"><td colspan="2"><table class="clientes-table"><thead><tr><th>CLIENTES</th><th>VALOR</th></tr></thead><tbody>`;
        html += rep.clientes.map(cli => `<tr><td>${cli.cliente}</td><td>R$ ${cli.valor.toLocaleString('pt-BR', {minimumFractionDigits:2})}</td></tr>`).join('');
        html += `<tr class="soma-row"><td>Total do Representante</td><td>R$ ${rep.total_representante.toLocaleString('pt-BR', {minimumFractionDigits:2})}</td></tr>`;
        html += '</tbody></table></td></tr>';
    });
    html += `<tr class="total-geral"><td>Total Geral</td><td><b>R$ ${totalGeral.toLocaleString('pt-BR', {minimumFractionDigits:2})}</b></td></tr>`;
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

async function loadDashboard() {
    dashboardDiv.innerHTML = '<em>Carregando dados...</em>';
    const res = await fetch('http://localhost:5000/dashboard_protheus');
    const data = await res.json();
    resumoProtheus = data;
    renderResumoTopo();
    renderDashboard(data.dados, dashboardDiv, 'aprovados');
}

async function loadDashboardCls() {
    dashboardClsDiv.innerHTML = '<em>Carregando dados da CLS...</em>';
    const res = await fetch('http://localhost:5000/dashboard_cls');
    const data = await res.json();
    resumoCls = data;
    renderResumoTopo();
    renderDashboard(data.dados, dashboardClsDiv, 'aprovacao');
} 