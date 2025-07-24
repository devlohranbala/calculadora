// Common JavaScript functions for Calculadora Kogui

// Global variables - using window object to avoid conflicts
window.appUserData = null;

// Utility function to get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Authentication check function
function checkAuthentication() {
    console.log('Verificando autenticação...');
    
    const userDataStr = localStorage.getItem('user_data');
    
    // Verificar se o usuário está autenticado
    fetch('/api/auth/profile/', {
        credentials: 'include'
    })
    .then(response => {
        console.log('Status da verificação do perfil:', response.status);
        if (!response.ok) {
            throw new Error(`Não autenticado - Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Perfil verificado com sucesso:', data);
        window.appUserData = data;
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = `👤 ${window.appUserData.nome}`;
        }
        localStorage.setItem('user_data', JSON.stringify(window.appUserData));
        
        // Call page-specific initialization if it exists
        if (typeof onAuthenticationSuccess === 'function') {
            onAuthenticationSuccess();
        }
    })
    .catch(error => {
        console.error('Erro na verificação de autenticação:', error);
        window.location.href = '/';
    });
}

// Logout function
async function logout() {
    try {
        await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        });
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
    }
    
    localStorage.removeItem('user_data');
    window.location.href = '/';
}

// Profile navigation function
function showProfile() {
    window.location.href = '/perfil/';
}

// Show error message function
function showError(message, elementId = 'errorMessage') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

// Show success message function
function showSuccess(message, elementId = 'successMessage') {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 5000);
    }
}

// Toggle loading state function
function toggleLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
    } else {
        element.classList.remove('loading');
    }
}

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page that requires authentication
    const requiresAuth = document.body.dataset.requiresAuth !== 'false';
    
    if (requiresAuth && window.location.pathname !== '/') {
        checkAuthentication();
    }
});

// Initialize on window load as well for compatibility
window.addEventListener('load', () => {
    const requiresAuth = document.body.dataset.requiresAuth !== 'false';
    
    if (requiresAuth && window.location.pathname !== '/') {
        checkAuthentication();
    }
});