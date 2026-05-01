let currentAuthTab = 'unlock';

async function init() {
    // Wait for pywebview to be ready
    if (window.pywebview && window.pywebview.api) {
        const vaults = await window.pywebview.api.list_vaults();
        const select = document.getElementById('vault-select');
        if (select) {
            select.innerHTML = vaults.map(v => `<option value="${v}">${v}</option>`).join('');
        }
    }
}

window.addEventListener('pywebviewready', init);

// Fallback for development if pywebviewready doesn't fire immediately
setTimeout(init, 500);

function switchAuthTab(tab) {
    currentAuthTab = tab;
    
    // UI Feedback for tabs
    const unlockBtn = document.getElementById('btn-tab-unlock');
    const createBtn = document.getElementById('btn-tab-create');
    
    unlockBtn.classList.toggle('bg-primary-container', tab === 'unlock');
    unlockBtn.classList.toggle('text-white', tab === 'unlock');
    unlockBtn.classList.toggle('text-on-surface-variant', tab !== 'unlock');

    createBtn.classList.toggle('bg-primary-container', tab === 'create');
    createBtn.classList.toggle('text-white', tab === 'create');
    createBtn.classList.toggle('text-on-surface-variant', tab !== 'create');
    
    // Show/Hide Forms
    document.getElementById('form-unlock').classList.toggle('hidden', tab !== 'unlock');
    document.getElementById('form-create').classList.toggle('hidden', tab !== 'create');
}

async function handleAuth() {
    if (currentAuthTab === 'unlock') {
        const name = document.getElementById('vault-select').value;
        const pass = document.getElementById('unlock-pass').value;
        if (!pass) return alert("Please enter password");
        
        const res = await window.pywebview.api.unlock_vault(name, pass);
        if (res.success) showDashboard();
        else alert(res.error);
    } else {
        const name = document.getElementById('create-name').value;
        const pass = document.getElementById('create-pass').value;
        if (!name || !pass) return alert("Fill all fields");
        
        const res = await window.pywebview.api.create_vault(name, pass);
        if (res.success) showDashboard();
        else alert(res.error);
    }
}

async function showDashboard() {
    document.getElementById('screen-login').classList.add('hidden');
    document.getElementById('screen-dashboard').classList.remove('hidden');
    refreshVault();
}

async function refreshVault() {
    const creds = await window.pywebview.api.get_credentials();
    const stats = document.getElementById('vault-stats');
    if (stats) stats.innerText = `Managing ${creds.length} secure credentials`;
    
    const grid = document.getElementById('credential-grid');
    if (!grid) return;
    
    if (creds.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center py-20 opacity-50">Vault is empty. Click Add New to start.</div>';
        return;
    }

    grid.innerHTML = creds.map((c, i) => `
        <div class="glass-panel p-6 rounded-2xl border border-white/5 hover:border-purple-500/50 transition-all group shadow-xl">
            <div class="flex justify-between items-start mb-6">
                <div class="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center">
                    <span class="material-symbols-outlined text-purple-400">shield</span>
                </div>
                <button onclick="deleteCred(${i})" class="text-slate-600 hover:text-red-500 transition-colors">
                    <span class="material-symbols-outlined">delete</span>
                </button>
            </div>
            <h3 class="text-xl font-bold text-white mb-1 font-['Space_Grotesk']">${c.site}</h3>
            <p class="text-[#d1c2d2] text-sm mb-6 opacity-70">${c.user}</p>
            <div class="flex items-center gap-3 pt-4 border-t border-white/5">
                <button onclick="copyToClipboard('${c.password}')" class="flex-1 py-2.5 bg-white/5 text-white rounded-full text-xs font-bold hover:bg-purple-600 transition-all">Copy Password</button>
            </div>
        </div>
    `).join('');
}

async function deleteCred(index) {
    if (confirm("Delete this credential permanently?")) {
        await window.pywebview.api.delete_credential(index);
        refreshVault();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    // Simple visual feedback could be added here
}

function showAddModal() { 
    document.getElementById('modal-add').classList.remove('hidden'); 
}

function closeModal() { 
    document.getElementById('modal-add').classList.add('hidden'); 
    // Clear inputs
    document.getElementById('add-site').value = '';
    document.getElementById('add-user').value = '';
    document.getElementById('add-pass').value = '';
}

async function togglePass(id) {
    const el = document.getElementById(id);
    const icon = document.getElementById(id + '-icon');
    if (el.type === 'password') {
        el.type = 'text';
        if (icon) icon.innerText = 'visibility_off';
    } else {
        el.type = 'password';
        if (icon) icon.innerText = 'visibility';
    }
}

async function generatePass() {
    const pass = await window.pywebview.api.generate_password();
    document.getElementById('add-pass').value = pass;
}

async function saveCredential() {
    const site = document.getElementById('add-site').value;
    const user = document.getElementById('add-user').value;
    const pass = document.getElementById('add-pass').value;
    
    if (site && user && pass) {
        await window.pywebview.api.add_credential(site, user, pass);
        closeModal();
        refreshVault();
    } else {
        alert("Please fill all fields");
    }
}

async function exportExcel() {
    const success = await window.pywebview.api.export_excel();
    if (success) {
        // Successful export notification could be handled here
    }
}
