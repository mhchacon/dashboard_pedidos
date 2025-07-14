// Usuários simulados
const USERS = {
  admin: 'admin123', // senha para admin
  gerencia: 'gerencia123' // senha para gerência
};

const loginContainer = document.getElementById('login-container');
const dashboard = document.getElementById('dashboard');
const adminUpload = document.getElementById('admin-upload');
const tabelaContainer = document.getElementById('tabela-container');
const tabelaResult = document.getElementById('tabela-result');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const userRole = document.getElementById('user-role');
const passwordInput = document.getElementById('password');
const loginError = document.getElementById('login-error');
const fileInput = document.getElementById('file-input');

let currentUser = null;

loginBtn.onclick = function() {
  const role = userRole.value;
  const pwd = passwordInput.value;
  if (USERS[role] && USERS[role] === pwd) {
    currentUser = role;
    loginContainer.style.display = 'none';
    dashboard.style.display = 'block';
    adminUpload.style.display = (role === 'admin') ? 'block' : 'none';
    tabelaResult.innerHTML = '';
    loginError.textContent = '';
  } else {
    loginError.textContent = 'Usuário ou senha inválidos.';
  }
};

logoutBtn.onclick = function() {
  currentUser = null;
  dashboard.style.display = 'none';
  loginContainer.style.display = 'block';
  passwordInput.value = '';
};

if (fileInput) {
  fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      processarPlanilha(file);
    }
  });
}

// Função para processar a planilha Protheus
function processarPlanilha(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const json = XLSX.utils.sheet_to_json(sheet, { defval: '' });
    const resultado = agruparDados(json);
    renderizarTabela(resultado);
  };
  reader.readAsArrayBuffer(file);
}

// Função para agrupar e filtrar os dados (a ser implementada)
function agruparDados(dados) {
  // Filtrar conforme regras
  const filtrados = dados.filter(linha => {
    // C5_CONDPAG != 103
    if (String(linha['C5_CONDPAG']).trim() === '103') return false;
    // C5_XOPFAT == 1 ou vazio
    const xopf = String(linha['C5_XOPFAT']).trim();
    if (!(xopf === '1' || xopf === '')) return false;
    // Precisa ter representante e cliente
    if (!linha['A3_NOME'] || !linha['C5_XNOME']) return false;
    // Precisa ter valor
    if (!linha['C6_VALOR']) return false;
    return true;
  });

  // Agrupar: { representante: { cliente: soma } }
  const agrupado = {};
  filtrados.forEach(linha => {
    const representante = String(linha['A3_NOME']).trim();
    const cliente = String(linha['C5_XNOME']).trim();
    // Converter valor (ponto para vírgula, depois para float)
    let valorStr = String(linha['C6_VALOR']).replace(',', '.');
    valorStr = valorStr.replace(/[^0-9.\-]/g, ''); // remove caracteres não numéricos
    const valor = parseFloat(valorStr) || 0;
    if (!agrupado[representante]) agrupado[representante] = {};
    if (!agrupado[representante][cliente]) agrupado[representante][cliente] = 0;
    agrupado[representante][cliente] += valor;
  });
  return agrupado;
}

// Função para renderizar a tabela (a ser implementada)
function renderizarTabela(agrupado) {
  if (!agrupado || Object.keys(agrupado).length === 0) {
    tabelaResult.innerHTML = '<p>Nenhum dado encontrado após o filtro.</p>';
    return;
  }
  let html = '<table><thead><tr><th>Representante</th><th>Cliente</th><th>Valor Total</th></tr></thead><tbody>';
  Object.keys(agrupado).forEach(representante => {
    html += `<tr class='representante-row'><td colspan='3'>${representante}</td></tr>`;
    let subtotal = 0;
    Object.keys(agrupado[representante]).forEach(cliente => {
      const valor = agrupado[representante][cliente];
      subtotal += valor;
      html += `<tr><td></td><td>${cliente}</td><td>R$ ${valor.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td></tr>`;
    });
    html += `<tr class='subtotal-row'><td colspan='2'>Subtotal ${representante}</td><td>R$ ${subtotal.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td></tr>`;
  });
  html += '</tbody></table>';
  tabelaResult.innerHTML = html;
} 