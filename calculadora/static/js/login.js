// Login page specific JavaScript functionality

let isLoginForm = true;

// Toggle between login and register forms
function toggleForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const toggleLink = document.getElementById('toggleLink');
    
    if (isLoginForm) {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        toggleLink.textContent = 'Já tem conta? Fazer login';
        isLoginForm = false;
    } else {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        toggleLink.textContent = 'Não tem conta? Criar uma';
        isLoginForm = true;
    }
    
    // Clear any error messages
    hideError();
    hideSuccess();
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const loginContainer = document.querySelector('.login-container');
    
    toggleLoading(loginContainer, true);
    hideError();
    
    try {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({
                email: formData.get('email'),
                senha: formData.get('senha')
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao fazer login');
        }
        
        // Store user data and redirect
        localStorage.setItem('user_data', JSON.stringify(data.user));
        showSuccess('Login realizado com sucesso! Redirecionando...');
        
        setTimeout(() => {
            window.location.href = '/calculadora/';
        }, 1500);
        
    } catch (error) {
        console.error('Erro no login:', error);
        showError(error.message);
    } finally {
        toggleLoading(loginContainer, false);
    }
}

// Handle register form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const loginContainer = document.querySelector('.login-container');
    
    // Validate password confirmation
    const senha = formData.get('senha');
    const confirmarSenha = formData.get('confirmar_senha');
    
    if (senha !== confirmarSenha) {
        showError('As senhas não coincidem');
        return;
    }
    
    toggleLoading(loginContainer, true);
    hideError();
    hideSuccess();
    
    try {
        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({
                nome: formData.get('nome'),
                email: formData.get('email'),
                senha: senha,
                confirmar_senha: confirmarSenha
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao registrar usuário');
        }
        
        showSuccess('Usuário registrado com sucesso! Você pode fazer login agora.');
        
        // Switch to login form after successful registration
        setTimeout(() => {
            toggleForm();
            // Pre-fill email field
            document.getElementById('email').value = formData.get('email');
        }, 2000);
        
    } catch (error) {
        console.error('Erro no registro:', error);
        showError(error.message);
    } finally {
        toggleLoading(loginContainer, false);
    }
}

// Utility functions for showing/hiding messages
function hideError() {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function hideSuccess() {
    const successElement = document.getElementById('successMessage');
    if (successElement) {
        successElement.style.display = 'none';
    }
}

// Initialize form event listeners
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const toggleLink = document.getElementById('toggleLink');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Add event listener for toggle link
    if (toggleLink) {
        toggleLink.addEventListener('click', function(event) {
            event.preventDefault();
            toggleForm();
        });
    }
    
    // Check if user is already logged in
    const userDataStr = localStorage.getItem('user_data');
    if (userDataStr) {
        try {
            const loginUserData = JSON.parse(userDataStr);
            // Verify with server only if we have valid user data
            if (loginUserData && loginUserData.id) {
                // Create an AbortController to handle request cancellation
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
                
                // Only check authentication if we have reasonable user data
                fetch('/api/auth/profile/', {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    signal: controller.signal
                })
                .then(response => {
                    clearTimeout(timeoutId);
                    if (response.ok) {
                        // User is already logged in, redirect to calculator
                        window.location.href = '/calculadora/';
                    } else if (response.status === 401 || response.status === 403) {
                        // Authentication failed, clear data
                        localStorage.removeItem('user_data');
                    } else {
                        // Other error, clear data
                        localStorage.removeItem('user_data');
                    }
                })
                .catch(error => {
                    clearTimeout(timeoutId);
                    // Handle aborted requests gracefully
                    if (error.name === 'AbortError') {
                        console.log('Authentication check timed out');
                    } else {
                        console.log('Authentication check failed:', error.message);
                    }
                    // Clear invalid session data on any error
                    localStorage.removeItem('user_data');
                });
            } else {
                // Invalid user data structure, clear it
                localStorage.removeItem('user_data');
            }
        } catch (e) {
            // Clear corrupted data
            console.log('Invalid user data in localStorage:', e.message);
            localStorage.removeItem('user_data');
        }
    }
});