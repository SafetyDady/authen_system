-- Authentication System Database Schema
-- PostgreSQL Database Schema for Enterprise Authentication System
-- Version: 1.0.0
-- Created: 2025-01-29

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('superadmin', 'admin1', 'admin2', 'admin3', 'user');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'locked', 'pending');
CREATE TYPE audit_action AS ENUM (
    'login', 'logout', 'login_failed', 'password_changed', 'profile_updated',
    'user_created', 'user_updated', 'user_deleted', 'user_locked', 'user_unlocked',
    'admin_created', 'admin_updated', 'admin_deleted', 'admin_locked', 'admin_unlocked',
    'role_changed', 'permissions_updated', 'password_reset_requested', 'password_reset_completed',
    'session_created', 'session_revoked', 'bulk_operation', 'system_settings_changed'
);

-- ============================================================================
-- ROLES TABLE
-- ============================================================================
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on roles
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_is_active ON roles(is_active);

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    role user_role NOT NULL DEFAULT 'user',
    status user_status NOT NULL DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    
    -- Password policy fields
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    password_expires_at TIMESTAMP WITH TIME ZONE,
    must_change_password BOOLEAN DEFAULT false,
    
    -- Account lockout fields
    failed_login_attempts INTEGER DEFAULT 0,
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    last_login TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    last_login_user_agent TEXT,
    email_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Create indexes on users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);
CREATE INDEX idx_users_email_verified ON users(email_verified);

-- ============================================================================
-- USER SESSIONS TABLE
-- ============================================================================
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) NOT NULL UNIQUE,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on user_sessions table
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_created_at ON user_sessions(created_at);

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action audit_action NOT NULL,
    resource VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    additional_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on audit_logs table
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================================
-- PASSWORD RESETS TABLE
-- ============================================================================
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT false,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on password_resets table
CREATE INDEX idx_password_resets_user_id ON password_resets(user_id);
CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_expires_at ON password_resets(expires_at);
CREATE INDEX idx_password_resets_is_used ON password_resets(is_used);

-- ============================================================================
-- SYSTEM SETTINGS TABLE
-- ============================================================================
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);

-- Create indexes on system_settings table
CREATE INDEX idx_system_settings_key ON system_settings(key);
CREATE INDEX idx_system_settings_is_public ON system_settings(is_public);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired sessions
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP OR is_active = false;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean expired password resets
CREATE OR REPLACE FUNCTION clean_expired_password_resets()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM password_resets 
    WHERE expires_at < CURRENT_TIMESTAMP OR is_used = true;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to log user activity
CREATE OR REPLACE FUNCTION log_user_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Log user creation
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (user_id, action, resource, resource_id, new_values)
        VALUES (NEW.created_by, 'user_created', 'users', NEW.id, row_to_json(NEW));
        RETURN NEW;
    END IF;
    
    -- Log user updates
    IF TG_OP = 'UPDATE' THEN
        -- Log role changes
        IF OLD.role != NEW.role THEN
            INSERT INTO audit_logs (user_id, action, resource, resource_id, old_values, new_values)
            VALUES (NEW.updated_by, 'role_changed', 'users', NEW.id, 
                   json_build_object('role', OLD.role), 
                   json_build_object('role', NEW.role));
        END IF;
        
        -- Log status changes
        IF OLD.status != NEW.status THEN
            INSERT INTO audit_logs (user_id, action, resource, resource_id, old_values, new_values)
            VALUES (NEW.updated_by, 
                   CASE 
                       WHEN NEW.status = 'locked' THEN 'user_locked'
                       WHEN OLD.status = 'locked' AND NEW.status = 'active' THEN 'user_unlocked'
                       ELSE 'user_updated'
                   END, 
                   'users', NEW.id, 
                   json_build_object('status', OLD.status), 
                   json_build_object('status', NEW.status));
        END IF;
        
        -- Log password changes
        IF OLD.password_hash != NEW.password_hash THEN
            INSERT INTO audit_logs (user_id, action, resource, resource_id)
            VALUES (NEW.id, 'password_changed', 'users', NEW.id);
        END IF;
        
        RETURN NEW;
    END IF;
    
    -- Log user deletion
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (user_id, action, resource, resource_id, old_values)
        VALUES (OLD.id, 'user_deleted', 'users', OLD.id, row_to_json(OLD));
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for user activity logging
CREATE TRIGGER log_user_activity_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION log_user_activity();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for user statistics
CREATE VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = true) as active_users,
    COUNT(*) FILTER (WHERE status = 'locked') as locked_users,
    COUNT(*) FILTER (WHERE role = 'superadmin') as superadmin_count,
    COUNT(*) FILTER (WHERE role IN ('admin1', 'admin2', 'admin3')) as admin_count,
    COUNT(*) FILTER (WHERE role = 'user') as regular_user_count,
    COUNT(*) FILTER (WHERE last_login > CURRENT_TIMESTAMP - INTERVAL '24 hours') as users_logged_in_24h,
    COUNT(*) FILTER (WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '30 days') as users_created_30d
FROM users;

-- View for session statistics
CREATE VIEW session_stats AS
SELECT 
    COUNT(*) as total_sessions,
    COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
    COUNT(*) FILTER (WHERE expires_at < CURRENT_TIMESTAMP) as expired_sessions,
    COUNT(DISTINCT user_id) as unique_users_with_sessions,
    AVG(EXTRACT(EPOCH FROM (last_used_at - created_at))/3600) as avg_session_duration_hours
FROM user_sessions;

-- View for audit log summary
CREATE VIEW audit_summary AS
SELECT 
    action,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(created_at) as first_occurrence,
    MAX(created_at) as last_occurrence
FROM audit_logs
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY action
ORDER BY count DESC;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_resets ENABLE ROW LEVEL SECURITY;

-- Create policies for users table
CREATE POLICY users_select_policy ON users
    FOR SELECT
    USING (
        -- Users can see their own record
        id = current_setting('app.current_user_id')::uuid
        OR
        -- Admins can see users they manage
        (
            current_setting('app.current_user_role') IN ('superadmin', 'admin1', 'admin2', 'admin3')
            AND (
                current_setting('app.current_user_role') = 'superadmin'
                OR role = 'user'
            )
        )
    );

CREATE POLICY users_update_policy ON users
    FOR UPDATE
    USING (
        -- Users can update their own record (limited fields)
        id = current_setting('app.current_user_id')::uuid
        OR
        -- Admins can update users they manage
        (
            current_setting('app.current_user_role') IN ('superadmin', 'admin1', 'admin2', 'admin3')
            AND (
                current_setting('app.current_user_role') = 'superadmin'
                OR role = 'user'
            )
        )
    );

-- Create policies for user_sessions table
CREATE POLICY user_sessions_policy ON user_sessions
    FOR ALL
    USING (
        user_id = current_setting('app.current_user_id')::uuid
        OR
        current_setting('app.current_user_role') = 'superadmin'
    );

-- Create policies for audit_logs table
CREATE POLICY audit_logs_select_policy ON audit_logs
    FOR SELECT
    USING (
        -- Users can see their own audit logs
        user_id = current_setting('app.current_user_id')::uuid
        OR
        -- Admins can see audit logs for users they manage
        current_setting('app.current_user_role') IN ('superadmin', 'admin1', 'admin2', 'admin3')
    );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'Main users table storing all user accounts';
COMMENT ON TABLE user_sessions IS 'Active user sessions with refresh tokens';
COMMENT ON TABLE audit_logs IS 'Audit trail for all user and system activities';
COMMENT ON TABLE password_resets IS 'Password reset tokens and their status';
COMMENT ON TABLE roles IS 'User roles and their permissions';
COMMENT ON TABLE system_settings IS 'System-wide configuration settings';

COMMENT ON COLUMN users.role IS 'User role: superadmin, admin1, admin2, admin3, or user';
COMMENT ON COLUMN users.status IS 'Account status: active, inactive, locked, or pending';
COMMENT ON COLUMN users.failed_login_attempts IS 'Number of consecutive failed login attempts';
COMMENT ON COLUMN users.locked_until IS 'Account locked until this timestamp';
COMMENT ON COLUMN users.password_expires_at IS 'When the current password expires';
COMMENT ON COLUMN users.must_change_password IS 'Whether user must change password on next login';

COMMENT ON VIEW user_stats IS 'Statistical summary of user accounts';
COMMENT ON VIEW session_stats IS 'Statistical summary of user sessions';
COMMENT ON VIEW audit_summary IS 'Summary of audit log activities in the last 30 days';

