-- Seed Data: 001_default_data.sql
-- Description: Insert default data for Authentication System
-- Version: 1.0.0
-- Created: 2025-01-29

-- This seed file creates:
-- - Default roles
-- - Default superadmin user
-- - Default admin users (admin1, admin2, admin3)
-- - Default system settings
-- - Sample regular users for testing

BEGIN;

-- Insert default roles
INSERT INTO roles (id, name, description, permissions, is_active) VALUES
(
    uuid_generate_v4(),
    'superadmin',
    'Super Administrator with full system access',
    '{
        "users": {"create": true, "read": true, "update": true, "delete": true},
        "admins": {"create": true, "read": true, "update": true, "delete": true},
        "roles": {"create": true, "read": true, "update": true, "delete": true},
        "system": {"read": true, "update": true, "backup": true, "restore": true},
        "audit": {"read": true, "export": true},
        "settings": {"read": true, "update": true}
    }',
    true
),
(
    uuid_generate_v4(),
    'admin1',
    'Admin 1 - User management for specific user groups',
    '{
        "users": {"create": true, "read": true, "update": true, "delete": false},
        "profile": {"read": true, "update": true},
        "reports": {"read": true, "export": true}
    }',
    true
),
(
    uuid_generate_v4(),
    'admin2',
    'Admin 2 - User management for specific user groups',
    '{
        "users": {"create": true, "read": true, "update": true, "delete": false},
        "profile": {"read": true, "update": true},
        "reports": {"read": true, "export": true}
    }',
    true
),
(
    uuid_generate_v4(),
    'admin3',
    'Admin 3 - User management for specific user groups',
    '{
        "users": {"create": true, "read": true, "update": true, "delete": false},
        "profile": {"read": true, "update": true},
        "reports": {"read": true, "export": true}
    }',
    true
),
(
    uuid_generate_v4(),
    'user',
    'Regular user with basic access',
    '{
        "profile": {"read": true, "update": true},
        "password": {"change": true}
    }',
    true
);

-- Insert default superadmin user
-- Password: admin123456 (hashed with bcrypt)
INSERT INTO users (
    id,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    is_active,
    email_verified,
    email_verified_at,
    created_at
) VALUES (
    uuid_generate_v4(),
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxYxHvby', -- admin123456
    'Super',
    'Admin',
    'superadmin',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert default admin users
-- Password for all: admin123456 (hashed with bcrypt)
INSERT INTO users (
    id,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    is_active,
    email_verified,
    email_verified_at,
    created_at
) VALUES 
(
    uuid_generate_v4(),
    'admin1@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxYxHvby', -- admin123456
    'Admin',
    'One',
    'admin1',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'admin2@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxYxHvby', -- admin123456
    'Admin',
    'Two',
    'admin2',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'admin3@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxYxHvby', -- admin123456
    'Admin',
    'Three',
    'admin3',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert sample regular users for testing
-- Password for all: user123456 (hashed with bcrypt)
INSERT INTO users (
    id,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    is_active,
    email_verified,
    email_verified_at,
    created_at
) VALUES 
(
    uuid_generate_v4(),
    'john.doe@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- user123456
    'John',
    'Doe',
    'user',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'jane.smith@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- user123456
    'Jane',
    'Smith',
    'user',
    'active',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'bob.wilson@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- user123456
    'Bob',
    'Wilson',
    'user',
    'active',
    true,
    false,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'alice.johnson@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- user123456
    'Alice',
    'Johnson',
    'user',
    'inactive',
    false,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    uuid_generate_v4(),
    'charlie.brown@example.com',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- user123456
    'Charlie',
    'Brown',
    'user',
    'locked',
    true,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP - INTERVAL '7 days'
);

-- Insert default system settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
-- Authentication settings
('auth.jwt_secret', '"your-super-secret-jwt-key-change-this-in-production"', 'JWT secret key for token signing', false),
('auth.jwt_expiry', '3600', 'JWT access token expiry in seconds (1 hour)', false),
('auth.refresh_token_expiry', '2592000', 'Refresh token expiry in seconds (30 days)', false),
('auth.max_login_attempts', '5', 'Maximum failed login attempts before account lockout', true),
('auth.lockout_duration', '1800', 'Account lockout duration in seconds (30 minutes)', true),
('auth.session_timeout', '3600', 'Session timeout in seconds (1 hour)', true),

-- Password policy settings
('password.min_length', '8', 'Minimum password length', true),
('password.require_uppercase', 'true', 'Require at least one uppercase letter', true),
('password.require_lowercase', 'true', 'Require at least one lowercase letter', true),
('password.require_numbers', 'true', 'Require at least one number', true),
('password.require_special_chars', 'true', 'Require at least one special character', true),
('password.expiry_days', '90', 'Password expiry in days (0 = never expires)', true),
('password.history_count', '5', 'Number of previous passwords to remember', true),

-- Email settings
('email.smtp_host', '"localhost"', 'SMTP server host', false),
('email.smtp_port', '587', 'SMTP server port', false),
('email.smtp_username', '""', 'SMTP username', false),
('email.smtp_password', '""', 'SMTP password', false),
('email.smtp_use_tls', 'true', 'Use TLS for SMTP connection', false),
('email.from_address', '"noreply@example.com"', 'Default from email address', false),
('email.from_name', '"Authentication System"', 'Default from name', false),

-- System settings
('system.name', '"Authentication System"', 'System name', true),
('system.version', '"1.0.0"', 'System version', true),
('system.maintenance_mode', 'false', 'Enable maintenance mode', true),
('system.registration_enabled', 'false', 'Allow new user registration', true),
('system.email_verification_required', 'true', 'Require email verification for new accounts', true),
('system.max_sessions_per_user', '5', 'Maximum concurrent sessions per user', true),

-- UI settings
('ui.theme', '"light"', 'Default UI theme', true),
('ui.logo_url', '""', 'Custom logo URL', true),
('ui.company_name', '"Your Company"', 'Company name for branding', true),
('ui.support_email', '"support@example.com"', 'Support email address', true),
('ui.terms_url', '""', 'Terms of service URL', true),
('ui.privacy_url', '""', 'Privacy policy URL', true),

-- Security settings
('security.enable_2fa', 'false', 'Enable two-factor authentication', true),
('security.force_https', 'true', 'Force HTTPS connections', true),
('security.session_cookie_secure', 'true', 'Use secure session cookies', false),
('security.csrf_protection', 'true', 'Enable CSRF protection', false),
('security.rate_limit_enabled', 'true', 'Enable API rate limiting', true),
('security.rate_limit_requests', '100', 'Rate limit requests per minute', true),

-- Audit settings
('audit.retention_days', '365', 'Audit log retention period in days', true),
('audit.enable_detailed_logging', 'true', 'Enable detailed audit logging', true),
('audit.log_failed_logins', 'true', 'Log failed login attempts', true),
('audit.log_password_changes', 'true', 'Log password changes', true),

-- Notification settings
('notifications.email_enabled', 'true', 'Enable email notifications', true),
('notifications.notify_admin_on_lockout', 'true', 'Notify admins when accounts are locked', true),
('notifications.notify_user_on_login', 'false', 'Notify users on successful login', true),
('notifications.notify_password_expiry', 'true', 'Notify users when password is about to expire', true),

-- Backup settings
('backup.auto_backup_enabled', 'false', 'Enable automatic database backups', true),
('backup.backup_frequency', '"daily"', 'Backup frequency (daily, weekly, monthly)', true),
('backup.retention_count', '7', 'Number of backups to retain', true),

-- API settings
('api.enable_swagger', 'true', 'Enable Swagger API documentation', true),
('api.cors_origins', '["http://localhost:3000", "http://localhost:5173"]', 'Allowed CORS origins', false),
('api.request_timeout', '30', 'API request timeout in seconds', true);

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, resource, resource_id, additional_info, created_at) 
SELECT 
    u.id,
    'user_created',
    'users',
    u.id,
    json_build_object('created_by', 'system', 'initial_setup', true),
    u.created_at
FROM users u;

-- Add initial login logs for demo
INSERT INTO audit_logs (user_id, action, resource, ip_address, user_agent, created_at)
SELECT 
    u.id,
    'login',
    'auth',
    '127.0.0.1'::inet,
    'Mozilla/5.0 (Demo Browser)',
    u.created_at + INTERVAL '1 hour'
FROM users u 
WHERE u.role IN ('superadmin', 'admin1', 'admin2', 'admin3')
AND u.email != 'charlie.brown@example.com';

COMMIT;

-- Display created accounts
SELECT 
    email,
    first_name,
    last_name,
    role,
    status,
    'Default password: admin123456 (for admins) or user123456 (for users)' as password_info
FROM users 
ORDER BY 
    CASE role 
        WHEN 'superadmin' THEN 1
        WHEN 'admin1' THEN 2
        WHEN 'admin2' THEN 3
        WHEN 'admin3' THEN 4
        ELSE 5
    END,
    email;

