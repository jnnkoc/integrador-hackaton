let adminToken = localStorage.getItem('isyshell_admin_token') || '';
let currentTab = 'scripts';

function saveToken() {
    adminToken = document.getElementById('adminToken').value.trim();
    localStorage.setItem('isyshell_admin_token', adminToken);
    document.getElementById('tokenStatus').textContent = '✓ Conectado';
    loadCurrentTab();
}

function adminHeaders() {
    return { 'Content-Type': 'application/json', 'X-Isy-Admin-Token': adminToken };
}

async function api(method, path, body = null) {
    const opts = { method, headers: adminHeaders() };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Erro desconhecido');
    }
    if (res.status === 204) return null;
    return res.json();
}

function showTab(tab, event) {
    if (event) event.preventDefault();
    document.querySelectorAll('[id^="tab-"]').forEach(el => el.classList.add('d-none'));
    document.getElementById('tab-' + tab).classList.remove('d-none');
    document.querySelectorAll('#mainTabs .nav-link').forEach(el => el.classList.remove('active'));
    if (event) event.target.classList.add('active');
    currentTab = tab;
    loadCurrentTab();
}

function loadCurrentTab() {
    if (currentTab === 'scripts') loadScripts();
    else if (currentTab === 'tokens') loadTokens();
    else if (currentTab === 'logs') loadLogs();
}

// ---- Scripts ----
async function loadScripts() {
    const el = document.getElementById('scriptsList');
    try {
        const scripts = await api('GET', '/api/v1/admin/scripts');
        if (!scripts.length) { el.innerHTML = '<p class="text-muted">Nenhum script cadastrado.</p>'; return; }
        el.innerHTML = `<table class="table table-hover table-bordered bg-white">
            <thead class="table-dark"><tr><th>Nome</th><th>Descrição</th><th>Parâmetros</th><th>Status</th><th>Ações</th></tr></thead>
            <tbody>${scripts.map(s => `<tr>
                <td><code>${s.name}</code></td>
                <td>${s.description || '-'}</td>
                <td>${(s.parameters || []).join(', ') || '-'}</td>
                <td><span class="badge ${s.is_active ? 'bg-success' : 'bg-secondary'}">${s.is_active ? 'Ativo' : 'Inativo'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1"
                        onclick='editScript(${JSON.stringify(s)})'>Editar</button>
                    <button class="btn btn-sm btn-outline-danger"
                        onclick="deleteScript('${s.id}')">Excluir</button>
                </td>
            </tr>`).join('')}</tbody></table>`;
    } catch (e) { el.innerHTML = `<div class="alert alert-danger">${e.message}</div>`; }
}

function showScriptForm() {
    ['scriptId','scriptName','scriptDescription','scriptParams','scriptContent'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('scriptActive').checked = true;
    document.getElementById('scriptFormTitle').textContent = 'Novo Script';
    document.getElementById('scriptForm').classList.remove('d-none');
}

function hideScriptForm() { document.getElementById('scriptForm').classList.add('d-none'); }

function editScript(s) {
    document.getElementById('scriptId').value = s.id;
    document.getElementById('scriptName').value = s.name;
    document.getElementById('scriptDescription').value = s.description;
    document.getElementById('scriptParams').value = (s.parameters || []).join(', ');
    document.getElementById('scriptContent').value = s.content;
    document.getElementById('scriptActive').checked = s.is_active;
    document.getElementById('scriptFormTitle').textContent = 'Editar Script';
    document.getElementById('scriptForm').classList.remove('d-none');
    document.getElementById('scriptForm').scrollIntoView({ behavior: 'smooth' });
}

async function saveScript() {
    const id = document.getElementById('scriptId').value;
    const data = {
        name: document.getElementById('scriptName').value,
        description: document.getElementById('scriptDescription').value,
        parameters: document.getElementById('scriptParams').value.split(',').map(p => p.trim()).filter(Boolean),
        content: document.getElementById('scriptContent').value,
        is_active: document.getElementById('scriptActive').checked,
    };
    try {
        if (id) await api('PUT', `/api/v1/admin/scripts/${id}`, data);
        else await api('POST', '/api/v1/admin/scripts', data);
        hideScriptForm();
        loadScripts();
    } catch (e) { alert('Erro: ' + e.message); }
}

async function deleteScript(id) {
    if (!confirm('Excluir este script?')) return;
    try { await api('DELETE', `/api/v1/admin/scripts/${id}`); loadScripts(); }
    catch (e) { alert('Erro: ' + e.message); }
}

// ---- Tokens ----
async function loadTokens() {
    const el = document.getElementById('tokensList');
    try {
        const tokens = await api('GET', '/api/v1/admin/tokens');
        if (!tokens.length) { el.innerHTML = '<p class="text-muted">Nenhum token cadastrado.</p>'; return; }
        el.innerHTML = `<table class="table table-hover table-bordered bg-white">
            <thead class="table-dark"><tr><th>Cliente</th><th>Token</th><th>Status</th><th>Criado em</th><th>Ações</th></tr></thead>
            <tbody>${tokens.map(t => `<tr>
                <td>${t.name}</td>
                <td><code class="small">${t.token}</code></td>
                <td><span class="badge ${t.is_active ? 'bg-success' : 'bg-secondary'}">${t.is_active ? 'Ativo' : 'Inativo'}</span></td>
                <td>${new Date(t.created_at).toLocaleString('pt-BR')}</td>
                <td>
                    <button class="btn btn-sm btn-outline-warning me-1"
                        onclick="toggleToken('${t.id}', ${!t.is_active})">${t.is_active ? 'Desativar' : 'Ativar'}</button>
                    <button class="btn btn-sm btn-outline-danger"
                        onclick="deleteToken('${t.id}')">Excluir</button>
                </td>
            </tr>`).join('')}</tbody></table>`;
    } catch (e) { el.innerHTML = `<div class="alert alert-danger">${e.message}</div>`; }
}

function showTokenForm() {
    document.getElementById('tokenName').value = '';
    document.getElementById('tokenForm').classList.remove('d-none');
}
function hideTokenForm() { document.getElementById('tokenForm').classList.add('d-none'); }

async function createToken() {
    const name = document.getElementById('tokenName').value.trim();
    if (!name) { alert('Informe o nome do cliente'); return; }
    try {
        const token = await api('POST', '/api/v1/admin/tokens', { name });
        hideTokenForm();
        loadTokens();
        alert(`Token criado com sucesso!\n\nCliente: ${token.name}\nToken: ${token.token}\n\nGuarde o token em local seguro — ele não será exibido novamente.`);
    } catch (e) { alert('Erro: ' + e.message); }
}

async function toggleToken(id, isActive) {
    try { await api('PATCH', `/api/v1/admin/tokens/${id}`, { is_active: isActive }); loadTokens(); }
    catch (e) { alert('Erro: ' + e.message); }
}

async function deleteToken(id) {
    if (!confirm('Excluir este token? Todas as execuções relacionadas serão mantidas no log.')) return;
    try { await api('DELETE', `/api/v1/admin/tokens/${id}`); loadTokens(); }
    catch (e) { alert('Erro: ' + e.message); }
}

// ---- Logs ----
async function loadLogs() {
    const el = document.getElementById('logsList');
    try {
        const logs = await api('GET', '/api/v1/admin/logs?limit=100');
        if (!logs.length) { el.innerHTML = '<p class="text-muted">Nenhuma execução registrada.</p>'; return; }
        el.innerHTML = `<table class="table table-hover table-bordered table-sm bg-white">
            <thead class="table-dark"><tr><th>Data/Hora</th><th>Script ID</th><th>Token ID</th><th>Status</th><th>Exit Code</th><th>stdout</th><th>stderr</th></tr></thead>
            <tbody>${logs.map(l => `<tr>
                <td class="small">${new Date(l.executed_at).toLocaleString('pt-BR')}</td>
                <td><code class="small">${l.script_id.substring(0,8)}…</code></td>
                <td><code class="small">${l.token_id.substring(0,8)}…</code></td>
                <td><span class="badge ${l.status === 'success' ? 'bg-success' : l.status === 'timeout' ? 'bg-warning text-dark' : 'bg-danger'}">${l.status}</span></td>
                <td>${l.exit_code}</td>
                <td><pre class="mb-0 small" style="max-width:200px;overflow:auto">${l.stdout || '-'}</pre></td>
                <td><pre class="mb-0 small text-danger" style="max-width:200px;overflow:auto">${l.stderr || '-'}</pre></td>
            </tr>`).join('')}</tbody></table>`;
    } catch (e) { el.innerHTML = `<div class="alert alert-danger">${e.message}</div>`; }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    if (adminToken) {
        document.getElementById('adminToken').value = adminToken;
        document.getElementById('tokenStatus').textContent = '✓ Token carregado';
        loadCurrentTab();
    }
});
