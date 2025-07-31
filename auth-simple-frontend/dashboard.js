// Dashboard JavaScript
let currentUser = null;
let currentSection = 'overview';

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load user data and initialize dashboard
    loadUserData();
    
    // Start real-time updates
    startRealTimeUpdates();
});

// Check Authentication
function checkAuthentication() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Sidebar toggle
    document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);
    document.getElementById('mobileMenuBtn').addEventListener('click', toggleMobileSidebar);
    
    // Logout buttons
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('headerLogoutBtn').addEventListener('click', logout);
    
    // User menu
    document.getElementById('userMenuBtn').addEventListener('click', toggleUserMenu);
    
    // Modal
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('modalOkBtn').addEventListener('click', closeModal);
    
    // Click outside to close dropdowns
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-menu')) {
            closeUserMenu();
        }
    });
}

// Load User Data
async function loadUserData() {
    try {
        const userData = localStorage.getItem('user_data');
        if (userData) {
            currentUser = JSON.parse(userData);
        } else {
            // Fetch user data from API
            const response = await window.AuthSystem.apiCall('/auth/me');
            if (response && response.ok) {
                currentUser = await response.json();
                localStorage.setItem('user_data', JSON.stringify(currentUser));
            }
        }
        
        if (currentUser) {
            updateUserInfo();
            generateNavigation();
            loadDashboardContent();
        }
        
    } catch (error) {
        console.error('Error loading user data:', error);
        showModal('ข้อผิดพลาด', 'ไม่สามารถโหลดข้อมูลผู้ใช้ได้');
    }
}

// Update User Info
function updateUserInfo() {
    const userName = `${currentUser.first_name} ${currentUser.last_name}`;
    const userRole = currentUser.role;
    
    document.getElementById('userName').textContent = userName;
    document.getElementById('userRole').textContent = getRoleDisplayName(userRole);
    document.getElementById('headerUserName').textContent = currentUser.first_name;
}

// Generate Navigation based on user role
function generateNavigation() {
    const nav = document.getElementById('sidebarNav');
    const role = currentUser.role;
    
    let navItems = [];
    
    // Common navigation items
    navItems.push({
        section: 'หลัก',
        items: [
            { id: 'overview', icon: '📊', text: 'ภาพรวม', href: '#overview' },
            { id: 'profile', icon: '👤', text: 'โปรไฟล์', href: '#profile' }
        ]
    });
    
    // Role-specific navigation
    if (role === 'superadmin') {
        navItems.push({
            section: 'การจัดการ',
            items: [
                { id: 'admin-management', icon: '👥', text: 'จัดการ Admin', href: '#admin-management' },
                { id: 'user-management', icon: '👤', text: 'จัดการผู้ใช้', href: '#user-management' },
                { id: 'system-settings', icon: '⚙️', text: 'ตั้งค่าระบบ', href: '#system-settings' },
                { id: 'audit-logs', icon: '📋', text: 'บันทึกการใช้งาน', href: '#audit-logs' }
            ]
        });
    } else if (['admin1', 'admin2', 'admin3'].includes(role)) {
        navItems.push({
            section: 'การจัดการ',
            items: [
                { id: 'user-management', icon: '👤', text: 'จัดการผู้ใช้', href: '#user-management' },
                { id: 'reports', icon: '📊', text: 'รายงาน', href: '#reports' }
            ]
        });
    }
    
    // Generate HTML
    let navHTML = '';
    navItems.forEach(section => {
        navHTML += `
            <div class="nav-section">
                <div class="nav-section-title">${section.section}</div>
                ${section.items.map(item => `
                    <a href="${item.href}" class="nav-item" data-section="${item.id}">
                        <span class="nav-item-icon">${item.icon}</span>
                        <span class="nav-item-text">${item.text}</span>
                    </a>
                `).join('')}
            </div>
        `;
    });
    
    nav.innerHTML = navHTML;
    
    // Add click listeners to navigation items
    nav.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            navigateToSection(section);
        });
    });
}

// Navigate to Section
function navigateToSection(section) {
    currentSection = section;
    
    // Update active navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    
    // Update breadcrumb
    updateBreadcrumb(section);
    
    // Load content
    loadSectionContent(section);
}

// Update Breadcrumb
function updateBreadcrumb(section) {
    const breadcrumb = document.getElementById('breadcrumb');
    const sectionNames = {
        'overview': 'ภาพรวม',
        'profile': 'โปรไฟล์',
        'admin-management': 'จัดการ Admin',
        'user-management': 'จัดการผู้ใช้',
        'system-settings': 'ตั้งค่าระบบ',
        'audit-logs': 'บันทึกการใช้งาน',
        'reports': 'รายงาน'
    };
    
    breadcrumb.innerHTML = `<span>Dashboard</span> <span>›</span> <span>${sectionNames[section] || section}</span>`;
}

// Load Dashboard Content
function loadDashboardContent() {
    // Default to overview
    navigateToSection('overview');
}

// Load Section Content
async function loadSectionContent(section) {
    const content = document.getElementById('content');
    
    // Show loading
    content.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner-large"></div>
            <p>กำลังโหลด...</p>
        </div>
    `;
    
    try {
        switch (section) {
            case 'overview':
                await loadOverviewContent();
                break;
            case 'profile':
                await loadProfileContent();
                break;
            case 'admin-management':
                await loadAdminManagementContent();
                break;
            case 'user-management':
                await loadUserManagementContent();
                break;
            case 'system-settings':
                await loadSystemSettingsContent();
                break;
            case 'audit-logs':
                await loadAuditLogsContent();
                break;
            case 'reports':
                await loadReportsContent();
                break;
            default:
                content.innerHTML = '<div class="content-section"><h2>ไม่พบหน้าที่ต้องการ</h2></div>';
        }
    } catch (error) {
        console.error('Error loading section content:', error);
        content.innerHTML = `
            <div class="content-section">
                <h2>เกิดข้อผิดพลาด</h2>
                <p>ไม่สามารถโหลดเนื้อหาได้ กรุณาลองใหม่อีกครั้ง</p>
            </div>
        `;
    }
}

// Load Overview Content
async function loadOverviewContent() {
    const content = document.getElementById('content');
    
    // Get statistics
    const stats = await getSystemStats();
    
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">ภาพรวมระบบ</h1>
            <p class="dashboard-subtitle">สถิติและข้อมูลสำคัญของระบบ Authentication</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">ผู้ใช้ทั้งหมด</div>
                    <div class="stat-icon" style="background: #dbeafe; color: #3b82f6;">👥</div>
                </div>
                <div class="stat-value">${stats.totalUsers}</div>
                <div class="stat-change positive">+${stats.newUsersToday} วันนี้</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">ผู้ใช้ออนไลน์</div>
                    <div class="stat-icon" style="background: #dcfce7; color: #059669;">🟢</div>
                </div>
                <div class="stat-value">${stats.onlineUsers}</div>
                <div class="stat-change positive">+${stats.onlineChange}%</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">การเข้าสู่ระบบวันนี้</div>
                    <div class="stat-icon" style="background: #fef3c7; color: #d97706;">🔑</div>
                </div>
                <div class="stat-value">${stats.todayLogins}</div>
                <div class="stat-change ${stats.loginChange >= 0 ? 'positive' : 'negative'}">${stats.loginChange >= 0 ? '+' : ''}${stats.loginChange}%</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">ความปลอดภัย</div>
                    <div class="stat-icon" style="background: ${stats.securityScore >= 90 ? '#dcfce7' : '#fef3c7'}; color: ${stats.securityScore >= 90 ? '#059669' : '#d97706'};">🛡️</div>
                </div>
                <div class="stat-value">${stats.securityScore}%</div>
                <div class="stat-change ${stats.securityScore >= 90 ? 'positive' : 'negative'}">${stats.securityScore >= 90 ? 'ปลอดภัย' : 'ต้องปรับปรุง'}</div>
            </div>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">กิจกรรมล่าสุด</h2>
                <div class="section-actions">
                    <button class="btn btn-secondary" onclick="refreshActivity()">🔄 รีเฟรช</button>
                </div>
            </div>
            <div id="recentActivity">
                ${generateRecentActivity(stats.recentActivity)}
            </div>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">ข้อมูลระบบ</h2>
            </div>
            <div class="system-info">
                <p><strong>เวอร์ชันระบบ:</strong> ${stats.systemVersion}</p>
                <p><strong>เซิร์ฟเวอร์:</strong> ${stats.serverStatus}</p>
                <p><strong>ฐานข้อมูล:</strong> ${stats.databaseStatus}</p>
                <p><strong>อัพเดทล่าสุด:</strong> ${stats.lastUpdate}</p>
            </div>
        </div>
    `;
}

// Load Profile Content
async function loadProfileContent() {
    const content = document.getElementById('content');
    
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">โปรไฟล์ผู้ใช้</h1>
            <p class="dashboard-subtitle">จัดการข้อมูลส่วนตัวและการตั้งค่าบัญชี</p>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">ข้อมูลส่วนตัว</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="editProfile()">✏️ แก้ไข</button>
                </div>
            </div>
            <div class="profile-info">
                <div class="profile-field">
                    <label>ชื่อ:</label>
                    <span>${currentUser.first_name}</span>
                </div>
                <div class="profile-field">
                    <label>นามสกุล:</label>
                    <span>${currentUser.last_name}</span>
                </div>
                <div class="profile-field">
                    <label>อีเมล:</label>
                    <span>${currentUser.email}</span>
                </div>
                <div class="profile-field">
                    <label>บทบาท:</label>
                    <span>${getRoleDisplayName(currentUser.role)}</span>
                </div>
                <div class="profile-field">
                    <label>สถานะ:</label>
                    <span class="status-badge ${currentUser.is_active ? 'active' : 'inactive'}">
                        ${currentUser.is_active ? 'ใช้งานได้' : 'ไม่ใช้งาน'}
                    </span>
                </div>
            </div>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">เปลี่ยนรหัสผ่าน</h2>
            </div>
            <form id="changePasswordForm" class="password-form">
                <div class="form-group">
                    <label>รหัสผ่านปัจจุบัน:</label>
                    <input type="password" id="currentPassword" required>
                </div>
                <div class="form-group">
                    <label>รหัสผ่านใหม่:</label>
                    <input type="password" id="newPassword" required>
                </div>
                <div class="form-group">
                    <label>ยืนยันรหัสผ่านใหม่:</label>
                    <input type="password" id="confirmPassword" required>
                </div>
                <button type="submit" class="btn btn-primary">เปลี่ยนรหัสผ่าน</button>
            </form>
        </div>
    `;
    
    // Add form listener
    document.getElementById('changePasswordForm').addEventListener('submit', handleChangePassword);
}

// Get System Stats
async function getSystemStats() {
    // Mock data for now - replace with actual API calls
    return {
        totalUsers: 1247,
        newUsersToday: 12,
        onlineUsers: 89,
        onlineChange: 15,
        todayLogins: 234,
        loginChange: 8,
        securityScore: 94,
        systemVersion: '1.0.0',
        serverStatus: 'ออนไลน์',
        databaseStatus: 'ปกติ',
        lastUpdate: '2025-01-31 10:30:00',
        recentActivity: [
            { user: 'admin1@example.com', action: 'เข้าสู่ระบบ', time: '10:30' },
            { user: 'user@example.com', action: 'อัพเดทโปรไฟล์', time: '10:25' },
            { user: 'admin2@example.com', action: 'สร้างผู้ใช้ใหม่', time: '10:20' }
        ]
    };
}

// Generate Recent Activity HTML
function generateRecentActivity(activities) {
    return activities.map(activity => `
        <div class="activity-item">
            <div class="activity-info">
                <strong>${activity.user}</strong> ${activity.action}
            </div>
            <div class="activity-time">${activity.time}</div>
        </div>
    `).join('');
}

// Get Role Display Name
function getRoleDisplayName(role) {
    const roleNames = {
        'superadmin': 'ผู้ดูแลระบบสูงสุด',
        'admin1': 'ผู้ดูแลระบบ 1',
        'admin2': 'ผู้ดูแลระบบ 2',
        'admin3': 'ผู้ดูแลระบบ 3',
        'user': 'ผู้ใช้ทั่วไป'
    };
    return roleNames[role] || role;
}

// Sidebar Functions
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('mobile-open');
}

// User Menu Functions
function toggleUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    userMenu.classList.toggle('open');
}

function closeUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    userMenu.classList.remove('open');
}

// Modal Functions
function showModal(title, message) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalMessage').textContent = message;
    document.getElementById('alertModal').classList.add('show');
}

function closeModal() {
    document.getElementById('alertModal').classList.remove('show');
}

// Logout Function
function logout() {
    if (confirm('คุณต้องการออกจากระบบหรือไม่?')) {
        window.AuthSystem.clearLoginData();
        window.location.href = 'index.html';
    }
}

// Real-time Updates
function startRealTimeUpdates() {
    // Update time every second
    updateHeaderTime();
    setInterval(updateHeaderTime, 1000);
    
    // Update stats every 30 seconds
    setInterval(() => {
        if (currentSection === 'overview') {
            loadOverviewContent();
        }
    }, 30000);
}

function updateHeaderTime() {
    const now = new Date();
    const timeString = now.toLocaleString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const headerTime = document.getElementById('headerTime');
    if (headerTime) {
        headerTime.textContent = timeString;
    }
}

// Load Admin Management Content
async function loadAdminManagementContent() {
    const content = document.getElementById('content');
    
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">จัดการ Admin</h1>
            <p class="dashboard-subtitle">จัดการผู้ดูแลระบบและสิทธิ์การเข้าถึง</p>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">รายชื่อ Admin</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="showAddAdminModal()">➕ เพิ่ม Admin</button>
                    <button class="btn btn-secondary" onclick="refreshAdminList()">🔄 รีเฟรช</button>
                </div>
            </div>
            <div id="adminListContainer">
                <div class="loading-content">
                    <div class="loading-spinner-large"></div>
                    <p>กำลังโหลดรายชื่อ Admin...</p>
                </div>
            </div>
        </div>
        
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">สถิติ Admin</h2>
            </div>
            <div class="admin-stats-grid">
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Admin ทั้งหมด</div>
                        <div class="stat-icon" style="background: #dbeafe; color: #3b82f6;">👥</div>
                    </div>
                    <div class="stat-value" id="totalAdmins">-</div>
                    <div class="stat-change">Admin1, Admin2, Admin3</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Admin ออนไลน์</div>
                        <div class="stat-icon" style="background: #dcfce7; color: #059669;">🟢</div>
                    </div>
                    <div class="stat-value" id="onlineAdmins">-</div>
                    <div class="stat-change" id="onlineAdminsChange">กำลังตรวจสอบ...</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Admin ใช้งานได้</div>
                        <div class="stat-icon" style="background: #fef3c7; color: #d97706;">✅</div>
                    </div>
                    <div class="stat-value" id="activeAdmins">-</div>
                    <div class="stat-change" id="activeAdminsChange">สถานะปกติ</div>
                </div>
            </div>
        </div>
    `;
    
    // Add CSS for admin stats grid
    if (!document.getElementById('adminStatsCSS')) {
        const style = document.createElement('style');
        style.id = 'adminStatsCSS';
        style.textContent = `
            .admin-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .admin-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            
            .admin-table th,
            .admin-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .admin-table th {
                background: #f8fafc;
                font-weight: 600;
                color: #374151;
            }
            
            .admin-table tr:hover {
                background: #f8fafc;
            }
            
            .status-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }
            
            .status-badge.active {
                background: #dcfce7;
                color: #059669;
            }
            
            .status-badge.inactive {
                background: #fee2e2;
                color: #dc2626;
            }
            
            .admin-actions {
                display: flex;
                gap: 8px;
            }
            
            .btn-small {
                padding: 4px 8px;
                font-size: 12px;
                border-radius: 4px;
            }
            
            .btn-edit {
                background: #3b82f6;
                color: white;
                border: none;
                cursor: pointer;
            }
            
            .btn-delete {
                background: #ef4444;
                color: white;
                border: none;
                cursor: pointer;
            }
            
            .btn-edit:hover {
                background: #2563eb;
            }
            
            .btn-delete:hover {
                background: #dc2626;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Load admin list
    await loadAdminList();
}

async function loadUserManagementContent() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">จัดการผู้ใช้</h1>
            <p class="dashboard-subtitle">จัดการบัญชีผู้ใช้และสิทธิ์การเข้าถึง</p>
        </div>
        <div class="content-section">
            <p>ฟีเจอร์นี้กำลังพัฒนา...</p>
        </div>
    `;
}

async function loadSystemSettingsContent() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">ตั้งค่าระบบ</h1>
            <p class="dashboard-subtitle">กำหนดค่าและการตั้งค่าระบบ</p>
        </div>
        <div class="content-section">
            <p>ฟีเจอร์นี้กำลังพัฒนา...</p>
        </div>
    `;
}

async function loadAuditLogsContent() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">บันทึกการใช้งาน</h1>
            <p class="dashboard-subtitle">ตรวจสอบกิจกรรมและการใช้งานระบบ</p>
        </div>
        <div class="content-section">
            <p>ฟีเจอร์นี้กำลังพัฒนา...</p>
        </div>
    `;
}

async function loadReportsContent() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="dashboard-header">
            <h1 class="dashboard-title">รายงาน</h1>
            <p class="dashboard-subtitle">รายงานและสถิติการใช้งาน</p>
        </div>
        <div class="content-section">
            <p>ฟีเจอร์นี้กำลังพัฒนา...</p>
        </div>
    `;
}

// Handle Change Password
async function handleChangePassword(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        showModal('ข้อผิดพลาด', 'รหัสผ่านใหม่ไม่ตรงกัน');
        return;
    }
    
    if (newPassword.length < 8) {
        showModal('ข้อผิดพลาด', 'รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร');
        return;
    }
    
    try {
        const response = await window.AuthSystem.apiCall('/auth/change-password', {
            method: 'POST',
            body: JSON.stringify({
                old_password: currentPassword,
                new_password: newPassword
            })
        });
        
        if (response && response.ok) {
            showModal('สำเร็จ', 'เปลี่ยนรหัสผ่านเรียบร้อยแล้ว');
            document.getElementById('changePasswordForm').reset();
        } else {
            const data = await response.json();
            showModal('ข้อผิดพลาด', data.detail || 'ไม่สามารถเปลี่ยนรหัสผ่านได้');
        }
    } catch (error) {
        console.error('Change password error:', error);
        showModal('ข้อผิดพลาด', 'เกิดข้อผิดพลาดในการเปลี่ยนรหัสผ่าน');
    }
}

// Utility functions
function refreshActivity() {
    if (currentSection === 'overview') {
        loadOverviewContent();
    }
}

function editProfile() {
    showModal('แจ้งเตือน', 'ฟีเจอร์แก้ไขโปรไฟล์กำลังพัฒนา');
}

// Admin Management Functions
async function loadAdminList() {
    try {
        const response = await window.AuthSystem.apiCall('/users/?role=admin');
        
        if (response && response.ok) {
            const admins = await response.json();
            displayAdminList(admins);
            updateAdminStats(admins);
        } else {
            // Use mock data if API fails
            const mockAdmins = [
                {
                    id: '1',
                    email: 'admin1@example.com',
                    first_name: 'Admin',
                    last_name: 'One',
                    role: 'admin1',
                    is_active: true,
                    created_at: '2025-01-01T00:00:00Z',
                    last_login: '2025-01-31T10:30:00Z'
                },
                {
                    id: '2',
                    email: 'admin2@example.com',
                    first_name: 'Admin',
                    last_name: 'Two',
                    role: 'admin2',
                    is_active: true,
                    created_at: '2025-01-01T00:00:00Z',
                    last_login: '2025-01-30T15:20:00Z'
                },
                {
                    id: '3',
                    email: 'admin3@example.com',
                    first_name: 'Admin',
                    last_name: 'Three',
                    role: 'admin3',
                    is_active: false,
                    created_at: '2025-01-01T00:00:00Z',
                    last_login: '2025-01-29T09:15:00Z'
                }
            ];
            displayAdminList(mockAdmins);
            updateAdminStats(mockAdmins);
        }
    } catch (error) {
        console.error('Error loading admin list:', error);
        document.getElementById('adminListContainer').innerHTML = `
            <div class="error-message">
                <p>❌ ไม่สามารถโหลดรายชื่อ Admin ได้</p>
                <button class="btn btn-primary" onclick="loadAdminList()">ลองใหม่</button>
            </div>
        `;
    }
}

function displayAdminList(admins) {
    const container = document.getElementById('adminListContainer');
    
    if (admins.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>ไม่มี Admin ในระบบ</p>
                <button class="btn btn-primary" onclick="showAddAdminModal()">เพิ่ม Admin แรก</button>
            </div>
        `;
        return;
    }
    
    const tableHTML = `
        <table class="admin-table">
            <thead>
                <tr>
                    <th>ชื่อ</th>
                    <th>อีเมล</th>
                    <th>บทบาท</th>
                    <th>สถานะ</th>
                    <th>เข้าสู่ระบบล่าสุด</th>
                    <th>การจัดการ</th>
                </tr>
            </thead>
            <tbody>
                ${admins.map(admin => `
                    <tr>
                        <td>${admin.first_name} ${admin.last_name}</td>
                        <td>${admin.email}</td>
                        <td>${getRoleDisplayName(admin.role)}</td>
                        <td>
                            <span class="status-badge ${admin.is_active ? 'active' : 'inactive'}">
                                ${admin.is_active ? 'ใช้งานได้' : 'ไม่ใช้งาน'}
                            </span>
                        </td>
                        <td>${formatDateTime(admin.last_login)}</td>
                        <td>
                            <div class="admin-actions">
                                <button class="btn-small btn-edit" onclick="editAdmin('${admin.id}')">แก้ไข</button>
                                <button class="btn-small btn-delete" onclick="deleteAdmin('${admin.id}', '${admin.email}')">ลบ</button>
                                <button class="btn-small ${admin.is_active ? 'btn-delete' : 'btn-edit'}" 
                                        onclick="toggleAdminStatus('${admin.id}', ${admin.is_active})">
                                    ${admin.is_active ? 'ปิดใช้งาน' : 'เปิดใช้งาน'}
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

function updateAdminStats(admins) {
    const totalAdmins = admins.length;
    const activeAdmins = admins.filter(admin => admin.is_active).length;
    const onlineAdmins = admins.filter(admin => {
        if (!admin.last_login) return false;
        const lastLogin = new Date(admin.last_login);
        const now = new Date();
        const hoursDiff = (now - lastLogin) / (1000 * 60 * 60);
        return hoursDiff < 1; // Consider online if logged in within last hour
    }).length;
    
    document.getElementById('totalAdmins').textContent = totalAdmins;
    document.getElementById('activeAdmins').textContent = activeAdmins;
    document.getElementById('onlineAdmins').textContent = onlineAdmins;
    
    document.getElementById('activeAdminsChange').textContent = 
        activeAdmins === totalAdmins ? 'ทั้งหมดใช้งานได้' : `${totalAdmins - activeAdmins} ไม่ใช้งาน`;
    document.getElementById('onlineAdminsChange').textContent = 
        onlineAdmins > 0 ? `${onlineAdmins} คนออนไลน์` : 'ไม่มีคนออนไลน์';
}

function formatDateTime(dateString) {
    if (!dateString) return 'ไม่เคยเข้าสู่ระบบ';
    
    const date = new Date(dateString);
    return date.toLocaleString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function refreshAdminList() {
    loadAdminList();
}

function showAddAdminModal() {
    const modalHTML = `
        <div class="modal show" id="addAdminModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>เพิ่ม Admin ใหม่</h3>
                    <button class="modal-close" onclick="closeAddAdminModal()">×</button>
                </div>
                <div class="modal-body">
                    <form id="addAdminForm">
                        <div class="form-group">
                            <label>ชื่อ:</label>
                            <input type="text" id="adminFirstName" required>
                        </div>
                        <div class="form-group">
                            <label>นามสกุล:</label>
                            <input type="text" id="adminLastName" required>
                        </div>
                        <div class="form-group">
                            <label>อีเมล:</label>
                            <input type="email" id="adminEmail" required>
                        </div>
                        <div class="form-group">
                            <label>บทบาท:</label>
                            <select id="adminRole" required>
                                <option value="">เลือกบทบาท</option>
                                <option value="admin1">Admin 1</option>
                                <option value="admin2">Admin 2</option>
                                <option value="admin3">Admin 3</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>รหัสผ่าน:</label>
                            <input type="password" id="adminPassword" required minlength="8">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeAddAdminModal()">ยกเลิก</button>
                    <button class="btn btn-primary" onclick="submitAddAdmin()">เพิ่ม Admin</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeAddAdminModal() {
    const modal = document.getElementById('addAdminModal');
    if (modal) {
        modal.remove();
    }
}

async function submitAddAdmin() {
    const firstName = document.getElementById('adminFirstName').value;
    const lastName = document.getElementById('adminLastName').value;
    const email = document.getElementById('adminEmail').value;
    const role = document.getElementById('adminRole').value;
    const password = document.getElementById('adminPassword').value;
    
    if (!firstName || !lastName || !email || !role || !password) {
        showModal('ข้อผิดพลาด', 'กรุณากรอกข้อมูลให้ครบถ้วน');
        return;
    }
    
    try {
        const response = await window.AuthSystem.apiCall('/users/', {
            method: 'POST',
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                role: role,
                password: password,
                is_active: true
            })
        });
        
        if (response && response.ok) {
            showModal('สำเร็จ', 'เพิ่ม Admin ใหม่เรียบร้อยแล้ว');
            closeAddAdminModal();
            loadAdminList();
        } else {
            const data = await response.json();
            showModal('ข้อผิดพลาด', data.detail || 'ไม่สามารถเพิ่ม Admin ได้');
        }
    } catch (error) {
        console.error('Error adding admin:', error);
        showModal('ข้อผิดพลาด', 'เกิดข้อผิดพลาดในการเพิ่ม Admin');
    }
}

async function editAdmin(adminId) {
    showModal('แจ้งเตือน', 'ฟีเจอร์แก้ไข Admin กำลังพัฒนา');
}

async function deleteAdmin(adminId, adminEmail) {
    if (!confirm(`คุณต้องการลบ Admin ${adminEmail} หรือไม่?`)) {
        return;
    }
    
    try {
        const response = await window.AuthSystem.apiCall(`/users/${adminId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showModal('สำเร็จ', 'ลบ Admin เรียบร้อยแล้ว');
            loadAdminList();
        } else {
            const data = await response.json();
            showModal('ข้อผิดพลาด', data.detail || 'ไม่สามารถลบ Admin ได้');
        }
    } catch (error) {
        console.error('Error deleting admin:', error);
        showModal('ข้อผิดพลาด', 'เกิดข้อผิดพลาดในการลบ Admin');
    }
}

async function toggleAdminStatus(adminId, currentStatus) {
    const action = currentStatus ? 'ปิดใช้งาน' : 'เปิดใช้งาน';
    
    if (!confirm(`คุณต้องการ${action} Admin นี้หรือไม่?`)) {
        return;
    }
    
    try {
        const response = await window.AuthSystem.apiCall(`/users/${adminId}`, {
            method: 'PUT',
            body: JSON.stringify({
                is_active: !currentStatus
            })
        });
        
        if (response && response.ok) {
            showModal('สำเร็จ', `${action} Admin เรียบร้อยแล้ว`);
            loadAdminList();
        } else {
            const data = await response.json();
            showModal('ข้อผิดพลาด', data.detail || `ไม่สามารถ${action} Admin ได้`);
        }
    } catch (error) {
        console.error('Error toggling admin status:', error);
        showModal('ข้อผิดพลาด', `เกิดข้อผิดพลาดในการ${action} Admin`);
    }
}

