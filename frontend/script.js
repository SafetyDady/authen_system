// Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const togglePasswordBtn = document.getElementById('togglePassword');
const loginBtn = document.getElementById('loginBtn');
const alertMessage = document.getElementById('alertMessage');
const rememberCheckbox = document.getElementById('remember');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check if already logged in
    checkExistingLogin();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load saved email if remember me was checked
    loadSavedCredentials();
});

// Setup Event Listeners
function setupEventListeners() {
    // Form submission
    loginForm.addEventListener('submit', handleLogin);
    
    // Password toggle
    togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
    
    // Enter key on inputs
    emailInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') passwordInput.focus();
    });
    
    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleLogin(e);
    });
    
    // Clear alerts when typing
    emailInput.addEventListener('input', clearAlert);
    passwordInput.addEventListener('input', clearAlert);
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    // Validation
    if (!email || !password) {
        showAlert('กรุณากรอกอีเมลและรหัสผ่าน', 'error');
        return;
    }
    
    if (!isValidEmail(email)) {
        showAlert('รูปแบบอีเมลไม่ถูกต้อง', 'error');
        return;
    }
    
    // Show loading
    setLoading(true);
    clearAlert();
    
    try {
        // Call login API
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.access_token) {
            // Login successful
            showAlert('เข้าสู่ระบบสำเร็จ!', 'success');
            
            // Save login data
            saveLoginData(data, email);
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
            
        } else {
            // Login failed
            const errorMessage = data.detail || data.message || 'เข้าสู่ระบบไม่สำเร็จ';
            showAlert(errorMessage, 'error');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        
        // Check if it's a network error
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบว่าเซิร์ฟเวอร์ทำงานอยู่', 'error');
        } else {
            showAlert('เกิดข้อผิดพลาดในการเข้าสู่ระบบ', 'error');
        }
    } finally {
        setLoading(false);
    }
}

// Save login data
function saveLoginData(data, email) {
    // Save to localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token || '');
    localStorage.setItem('user_data', JSON.stringify(data.user || {}));
    localStorage.setItem('login_time', new Date().toISOString());
    
    // Save email if remember me is checked
    if (rememberCheckbox.checked) {
        localStorage.setItem('remembered_email', email);
    } else {
        localStorage.removeItem('remembered_email');
    }
}

// Load saved credentials
function loadSavedCredentials() {
    const rememberedEmail = localStorage.getItem('remembered_email');
    if (rememberedEmail) {
        emailInput.value = rememberedEmail;
        rememberCheckbox.checked = true;
        passwordInput.focus();
    }
}

// Check existing login
function checkExistingLogin() {
    const token = localStorage.getItem('access_token');
    const loginTime = localStorage.getItem('login_time');
    
    if (token && loginTime) {
        // Check if token is still valid (less than 24 hours old)
        const loginDate = new Date(loginTime);
        const now = new Date();
        const hoursDiff = (now - loginDate) / (1000 * 60 * 60);
        
        if (hoursDiff < 24) {
            // Token might still be valid, redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            // Token expired, clear storage
            clearLoginData();
        }
    }
}

// Clear login data
function clearLoginData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('login_time');
}

// Toggle password visibility
function togglePasswordVisibility() {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    
    // Change icon
    togglePasswordBtn.textContent = type === 'password' ? '👁️' : '🙈';
}

// Show alert message
function showAlert(message, type = 'info') {
    alertMessage.textContent = message;
    alertMessage.className = `alert ${type} show`;
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        clearAlert();
    }, 5000);
}

// Clear alert message
function clearAlert() {
    alertMessage.className = 'alert';
    alertMessage.textContent = '';
}

// Set loading state
function setLoading(loading) {
    if (loading) {
        loginBtn.classList.add('loading');
        loginBtn.disabled = true;
    } else {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utility function to get user role
function getUserRole() {
    const userData = localStorage.getItem('user_data');
    if (userData) {
        const user = JSON.parse(userData);
        return user.role || 'user';
    }
    return null;
}

// Utility function to get access token
function getAccessToken() {
    return localStorage.getItem('access_token');
}

// Utility function to make authenticated API calls
async function apiCall(endpoint, options = {}) {
    const token = getAccessToken();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);
    
    // Handle token expiration
    if (response.status === 401) {
        clearLoginData();
        window.location.href = 'index.html';
        return null;
    }
    
    return response;
}

// Export functions for use in other files
window.AuthSystem = {
    getUserRole,
    getAccessToken,
    apiCall,
    clearLoginData
};

