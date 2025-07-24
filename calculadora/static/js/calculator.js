// Calculator-specific JavaScript functionality

let currentInput = '0';
let shouldResetDisplay = false;

// Calculator display functions
function appendToDisplay(value) {
    const display = document.getElementById('display');
    
    if (shouldResetDisplay) {
        currentInput = '';
        shouldResetDisplay = false;
    }
    
    if (currentInput === '0' && value !== '.') {
        currentInput = value;
    } else {
        currentInput += value;
    }
    
    display.textContent = currentInput;
}

function clearDisplay() {
    currentInput = '0';
    document.getElementById('display').textContent = currentInput;
}

function clearEntry() {
    currentInput = currentInput.slice(0, -1) || '0';
    document.getElementById('display').textContent = currentInput;
}

// Calculate function
async function calculate() {
    try {
        const expression = currentInput;
        
        const response = await fetch('/api/operacoes/calcular/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({ operacao: expression })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao calcular');
        }
        
        const data = await response.json();
        const result = data.resultado;
        
        document.getElementById('display').textContent = result;
        currentInput = result;
        shouldResetDisplay = true;
        
        // Adicionar ao histórico
        addToHistory(expression, result);
        
    } catch (error) {
        document.getElementById('display').textContent = 'Erro';
        currentInput = '0';
        console.error('Erro ao calcular:', error);
    }
}

// History functions
function addToHistory(expression, result) {
    const historyItems = document.getElementById('historyItems');
    const timestamp = new Date().toLocaleString('pt-BR');
    
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.innerHTML = `
        <div class="expression">${expression}</div>
        <div class="result">= ${result}</div>
        <div class="timestamp">${timestamp}</div>
    `;
    
    historyItems.insertBefore(historyItem, historyItems.firstChild);
}

async function loadHistory() {
    const historyItems = document.getElementById('historyItems');
    
    try {
        console.log('Carregando histórico...');
        
        const response = await fetch('/api/operacoes/', {
            credentials: 'include'
        });
        
        console.log('Status da resposta:', response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Token expirado ou inválido');
                historyItems.innerHTML = '<div class="loading">Sessão expirada. Faça login novamente.</div>';
                setTimeout(() => logout(), 2000);
                return;
            }
            
            const errorText = await response.text();
            console.error('Erro na resposta:', errorText);
            throw new Error(`Erro ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Dados recebidos:', data);
        
        // Verificar se os dados estão em formato paginado
        let operacoes = data;
        if (data && typeof data === 'object' && data.results) {
            operacoes = data.results;
            console.log('Dados paginados detectados, usando results:', operacoes);
        }
        
        if (!Array.isArray(operacoes)) {
            console.error('Formato de dados inválido:', data);
            console.error('Tipo de dados recebido:', typeof data);
            historyItems.innerHTML = `<div class="loading">Erro: formato de dados inválido. Tipo recebido: ${typeof data}</div>`;
            return;
        }
        
        if (operacoes.length === 0) {
            historyItems.innerHTML = '<div class="loading">Nenhuma operação realizada ainda.</div>';
            return;
        }
        
        historyItems.innerHTML = '';
        
        operacoes.forEach((operacao, index) => {
            try {
                const timestamp = operacao.data_inclusao ? 
                    new Date(operacao.data_inclusao).toLocaleString('pt-BR') : 
                    'Data não disponível';
                
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div class="expression">${operacao.operacao || 'N/A'}</div>
                    <div class="result">= ${operacao.resultado || 'N/A'}</div>
                    <div class="timestamp">${timestamp}</div>
                `;
                historyItems.appendChild(historyItem);
            } catch (itemError) {
                console.error(`Erro ao processar item ${index}:`, itemError, operacao);
            }
        });
        
        console.log('Histórico carregado com sucesso');
        
    } catch (error) {
        console.error('Erro detalhado ao carregar histórico:', error);
        historyItems.innerHTML = `<div class="loading">Erro ao carregar histórico: ${error.message}</div>`;
    }
}

async function clearHistory() {
    if (confirm('Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.')) {
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

            const data = await response.json();
            document.getElementById('historyItems').innerHTML = '<div class="loading">Nenhuma operação realizada ainda.</div>';
            alert(`Histórico limpo com sucesso! ${data.operacoes_deletadas} operações foram removidas.`);
            
        } catch (error) {
            console.error('Erro ao limpar histórico:', error);
            alert('Erro ao limpar histórico. Tente novamente.');
        }
    }
}

// Keyboard support
document.addEventListener('keydown', (event) => {
    const key = event.key;
    
    if (key >= '0' && key <= '9' || key === '.') {
        appendToDisplay(key);
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendToDisplay(key);
    } else if (key === 'Enter' || key === '=') {
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key === 'Backspace') {
        clearEntry();
    }
});

// Page-specific initialization function called by common.js
function onAuthenticationSuccess() {
    loadHistory();
}