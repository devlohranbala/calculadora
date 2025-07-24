// Profile page specific JavaScript functionality
// Using global namespace to avoid variable conflicts
let currentPage = 1;
let totalPages = 1;
let isEditMode = false;
const itemsPerPage = 10;

// Initialize profile page
document.addEventListener('DOMContentLoaded', () => {
    console.log('Profile page DOM loaded');
    checkAuthentication();
});

window.addEventListener('load', () => {
    console.log('Profile page fully loaded');
    if (!window.appUserData) {
        checkAuthentication();
    }
});

function checkAuthentication() {
    const userDataStr = localStorage.getItem('user_data');
    
    // Verificar se o usuário está autenticado
    fetch('/api/auth/profile/', {
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Não autenticado');
        }
        return response.json();
    })
    .then(data => {
        window.appUserData = data;
        localStorage.setItem('user_data', JSON.stringify(window.appUserData));
        loadProfile();
        loadHistoryWithPagination();
    })
    .catch(error => {
        console.error('Erro na verificação de autenticação:', error);
        window.location.href = '/';
    });
}

async function loadProfile() {
    try {
        const response = await fetch('/api/auth/profile/', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar perfil');
        }

        const data = await response.json();
        window.appUserData = data;

        // Atualizar interface
        document.getElementById('profileName').textContent = data.nome;
        document.getElementById('profileEmail').textContent = data.email;
        document.getElementById('nameValue').textContent = data.nome;
        document.getElementById('emailValue').textContent = data.email;
        
        // Gerar avatar com inicial do nome
        const initial = data.nome.charAt(0).toUpperCase();
        document.getElementById('profileAvatar').textContent = initial;

        // Formatar data de cadastro
        const dataCadastro = new Date(data.data_cadastro);
        const opcoes = { year: 'numeric', month: 'long' };
        const dataFormatada = dataCadastro.toLocaleDateString('pt-BR', opcoes);
        document.getElementById('memberSince').textContent = dataFormatada;

    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        if (error.message.includes('401')) {
            logout();
        }
    }
}

async function loadHistoryWithPagination() {
    try {
        const response = await fetch('/api/operacoes/', {
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        let operacoes = Array.isArray(data) ? data : (data.results || []);

        // Armazenar operações globalmente para paginação
        window.allOperations = operacoes;

        // Calcular estatísticas
        calculateStats(operacoes);

        // Implementar paginação manual
        totalPages = Math.ceil(operacoes.length / itemsPerPage);
        displayHistory(operacoes);
        updatePagination();

    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        document.getElementById('historyItems').innerHTML = 
            `<div class="error">Erro ao carregar histórico: ${error.message}</div>`;
        
        // Resetar estatísticas em caso de erro
        document.getElementById('totalOperations').textContent = '0';
        document.getElementById('todayOperations').textContent = '0';
        document.getElementById('weekOperations').textContent = '0';
    }
}

function calculateStats(operacoes) {
    const total = operacoes.length;
    const today = new Date();
    const todayStr = today.toDateString();
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    const todayCount = operacoes.filter(op => {
        const opDate = new Date(op.data_inclusao);
        return opDate.toDateString() === todayStr;
    }).length;

    const weekCount = operacoes.filter(op => {
        const opDate = new Date(op.data_inclusao);
        return opDate >= weekAgo;
    }).length;

    document.getElementById('totalOperations').textContent = total;
    document.getElementById('todayOperations').textContent = todayCount;
    document.getElementById('weekOperations').textContent = weekCount;
}

function displayHistory(operacoes) {
    const historyItems = document.getElementById('historyItems');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageOperacoes = operacoes.slice(startIndex, endIndex);

    if (pageOperacoes.length === 0) {
        historyItems.innerHTML = '<div class="loading">Nenhuma operação encontrada.</div>';
        return;
    }

    historyItems.innerHTML = '';
    pageOperacoes.forEach(operacao => {
        const timestamp = new Date(operacao.data_inclusao).toLocaleString('pt-BR');
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="expression">${operacao.operacao}</div>
            <div class="result">= ${operacao.resultado}</div>
            <div class="timestamp">${timestamp}</div>
        `;
        historyItems.appendChild(historyItem);
    });
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');

    if (totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }

    pagination.style.display = 'flex';
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
    pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        if (window.allOperations) {
            displayHistory(window.allOperations);
            updatePagination();
        } else {
            loadHistoryWithPagination();
        }
    }
}

function editField(fieldName) {
    if (isEditMode) return;

    isEditMode = true; // Definir modo de edição como ativo

    const valueElement = document.getElementById(fieldName === 'nome' ? 'nameValue' : 'emailValue');
    const currentValue = valueElement.textContent;

    const input = document.createElement('input');
    input.type = fieldName === 'email' ? 'email' : 'text';
    input.className = 'edit-input';
    input.value = currentValue;
    input.required = true;

    if (fieldName === 'email') {
        input.pattern = '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$';
    }

    const actions = document.createElement('div');
    actions.className = 'edit-actions';
    actions.innerHTML = `
        <button class="btn btn-save" onclick="saveField('${fieldName}', this)">Salvar</button>
        <button class="btn btn-cancel" onclick="cancelEdit('${fieldName}')">Cancelar</button>
    `;

    valueElement.innerHTML = '';
    valueElement.appendChild(input);
    valueElement.appendChild(actions);
    input.focus();
}

async function saveField(fieldName, button) {
    const valueElement = document.getElementById(fieldName === 'nome' ? 'nameValue' : 'emailValue');
    const input = valueElement.querySelector('input');
    const newValue = input.value.trim();

    if (!newValue) {
        alert('O campo não pode estar vazio');
        return;
    }

    if (fieldName === 'email' && !isValidEmail(newValue)) {
        alert('Por favor, insira um email válido');
        return;
    }

    try {
        button.disabled = true;
        button.textContent = 'Salvando...';

        const updateData = {};
        updateData[fieldName] = newValue;

        const response = await fetch(`/api/usuarios/${window.appUserData.id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            throw new Error('Erro ao atualizar perfil');
        }

        const updatedData = await response.json();
        window.appUserData = updatedData;

        // Atualizar localStorage
        localStorage.setItem('user_data', JSON.stringify(updatedData));

        // Atualizar interface
        valueElement.innerHTML = newValue;
        valueElement.className = 'info-value editable';
        valueElement.onclick = () => editField(fieldName);

        if (fieldName === 'nome') {
            document.getElementById('profileName').textContent = newValue;
            document.getElementById('profileAvatar').textContent = newValue.charAt(0).toUpperCase();
        } else if (fieldName === 'email') {
            document.getElementById('profileEmail').textContent = newValue;
        }

        alert('Perfil atualizado com sucesso!');

    } catch (error) {
        console.error('Erro ao salvar:', error);
        alert('Erro ao atualizar perfil. Tente novamente.');
    } finally {
        // Sempre sair do modo de edição, mesmo em caso de erro
        isEditMode = false;
    }
}

function cancelEdit(fieldName) {
    const valueElement = document.getElementById(fieldName === 'nome' ? 'nameValue' : 'emailValue');
    const originalValue = window.appUserData[fieldName];
    
    // Restaurar o valor original
    valueElement.innerHTML = originalValue;
    valueElement.className = 'info-value editable';
    
    // Restaurar a funcionalidade de clique
    valueElement.onclick = () => editField(fieldName);
    
    // Sair do modo de edição
    isEditMode = false;
}

function isValidEmail(email) {
    const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
    return emailRegex.test(email);
}



async function clearHistory() {
    if (!confirm('Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        const response = await fetch('/api/operacoes/limpar_historico/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao limpar histórico');
        }

        // Recarregar histórico
        currentPage = 1;
        loadHistoryWithPagination();
        alert('Histórico limpo com sucesso!');

    } catch (error) {
        console.error('Erro ao limpar histórico:', error);
        alert('Erro ao limpar histórico. Tente novamente.');
    }
}

async function deletarConta() {
    // Primeira confirmação
    if (!confirm('⚠️ ATENÇÃO: Você está prestes a apagar sua conta permanentemente!\n\nEsta ação irá:\n• Deletar todos os seus dados\n• Remover todo o histórico de operações\n• Não poderá ser desfeita\n\nTem certeza que deseja continuar?')) {
        return;
    }

    // Segunda confirmação para maior segurança
    const confirmacao = prompt('Para confirmar a exclusão da sua conta, digite "DELETAR" (em maiúsculas):');
    
    if (confirmacao !== 'DELETAR') {
        alert('Exclusão cancelada. Texto de confirmação incorreto.');
        return;
    }

    try {
        const response = await fetch('/api/auth/deletar-conta/', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao deletar conta');
        }

        const data = await response.json();
        
        // Limpar dados locais
        localStorage.removeItem('user_data');
        
        alert('Conta deletada com sucesso! Você será redirecionado para a página inicial.');
        
        // Redirecionar para a página de login
        window.location.href = '/';

    } catch (error) {
        console.error('Erro ao deletar conta:', error);
        alert('Erro ao deletar conta. Tente novamente ou entre em contato com o suporte.');
    }
}