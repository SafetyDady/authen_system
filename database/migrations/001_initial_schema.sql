-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema for Authentication System
-- Version: 1.0.0
-- Created: 2025-01-29
-- Author: Authentication System

-- This migration creates the initial database schema including:
-- - User management tables
-- - Authentication and session management
-- - Audit logging system
-- - Password reset functionality
-- - System settings

BEGIN;

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

-- Create roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
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

-- Create user_sessions table
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

-- Create audit_logs table
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

-- Create password_resets table
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT false,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create system_settings table
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

-- Create indexes
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_is_active ON roles(is_active);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);
CREATE INDEX idx_users_email_verified ON users(email_verified);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_created_at ON user_sessions(created_at);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX idx_password_resets_user_id ON password_resets(user_id);
CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_expires_at ON password_resets(expires_at);
CREATE INDEX idx_password_resets_is_used ON password_resets(is_used);

CREATE INDEX idx_system_settings_key ON system_settings(key);
CREATE INDEX idx_system_settings_is_public ON system_settings(is_public);

-- Create functions and triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create utility functions
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

-- Create audit logging function
CREATE OR REPLACE FUNCTION log_user_activity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (user_id, action, resource, resource_id, new_values)
        VALUES (NEW.created_by, 'user_created', 'users', NEW.id, row_to_json(NEW));
        RETURN NEW;
    END IF;
    
    IF TG_OP = 'UPDATE' THEN
        IF OLD.role != NEW.role THEN
            INSERT INTO audit_logs (user_id, action, resource, resource_id, old_values, new_values)
            VALUES (NEW.updated_by, 'role_changed', 'users', NEW.id, 
                   json_build_object('role', OLD.role), 
                   json_build_object('role', NEW.role));
        END IF;
        
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
        
        IF OLD.password_hash != NEW.password_hash THEN
            INSERT INTO audit_logs (user_id, action, resource, resource_id)
            VALUES (NEW.id, 'password_changed', 'users', NEW.id);
        END IF;
        
        RETURN NEW;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (user_id, action, resource, resource_id, old_values)
        VALUES (OLD.id, 'user_deleted', 'users', OLD.id, row_to_json(OLD));
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_user_activity_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION log_user_activity();

-- Create views
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

CREATE VIEW session_stats AS
SELECT 
    COUNT(*) as total_sessions,
    COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
    COUNT(*) FILTER (WHERE expires_at < CURRENT_TIMESTAMP) as expired_sessions,
    COUNT(DISTINCT user_id) as unique_users_with_sessions,
    AVG(EXTRACT(EPOCH FROM (last_used_at - created_at))/3600) as avg_session_duration_hours
FROM user_sessions;

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

-- Add comments
COMMENT ON TABLE users IS 'Main users table storing all user accounts';
COMMENT ON TABLE user_sessions IS 'Active user sessions with refresh tokens';
COMMENT ON TABLE audit_logs IS 'Audit trail for all user and system activities';
COMMENT ON TABLE password_resets IS 'Password reset tokens and their status';
COMMENT ON TABLE roles IS 'User roles and their permissions';
COMMENT ON TABLE system_settings IS 'System-wide configuration settings';

-- Record migration
INSERT INTO system_settings (key, value, description, is_public) VALUES
('migration_version', '"001"', 'Current database migration version', false),
('migration_001_applied_at', to_jsonb(CURRENT_TIMESTAMP), 'Timestamp when migration 001 was applied', false);

COMMIT;

