# API Documentation - Authentication System

This document provides comprehensive documentation for the Authentication System REST API. The API is built with FastAPI and follows RESTful principles with OpenAPI 3.0 specification.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [Examples](#examples)
8. [SDKs and Client Libraries](#sdks-and-client-libraries)

## API Overview

### Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

### API Version
- **Current Version**: v1
- **API Specification**: OpenAPI 3.0
- **Interactive Documentation**: Available at `/docs` endpoint

### Content Type
- **Request**: `application/json`
- **Response**: `application/json`

### HTTP Methods
The API uses standard HTTP methods:
- `GET` - Retrieve resources
- `POST` - Create new resources
- `PUT` - Update existing resources (complete replacement)
- `PATCH` - Partial update of resources
- `DELETE` - Remove resources

## Authentication

The API uses JWT (JSON Web Token) based authentication with access and refresh tokens.

### Authentication Flow

1. **Login**: Send credentials to `/auth/login`
2. **Receive Tokens**: Get access token (short-lived) and refresh token (long-lived)
3. **Use Access Token**: Include in Authorization header for protected endpoints
4. **Refresh Token**: Use refresh token to get new access token when expired

### Token Types

#### Access Token
- **Purpose**: Authenticate API requests
- **Lifetime**: 1 hour (configurable)
- **Usage**: Include in Authorization header
- **Format**: `Bearer <access_token>`

#### Refresh Token
- **Purpose**: Obtain new access tokens
- **Lifetime**: 30 days (configurable)
- **Usage**: Send to `/auth/refresh` endpoint
- **Storage**: Secure HTTP-only cookie (recommended) or local storage

### Authorization Header

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Token Payload

Access tokens contain the following claims:

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin1",
  "permissions": ["users:read", "users:write"],
  "exp": 1643723400,
  "iat": 1643719800,
  "jti": "token_id"
}
```

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses.

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no content returned |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2025-01-29T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `TOKEN_EXPIRED` | Access token has expired |
| `TOKEN_INVALID` | Invalid or malformed token |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RESOURCE_CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `ACCOUNT_LOCKED` | User account is locked |
| `PASSWORD_EXPIRED` | Password has expired |

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage.

### Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| User Management | 100 requests | 1 minute |
| General API | 1000 requests | 1 hour |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643723400
X-RateLimit-Window: 60
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 60
  }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/login

Authenticate user and receive access and refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin1",
    "permissions": ["users:read", "users:write"]
  }
}
```

**Errors:**
- `400` - Invalid request data
- `401` - Invalid credentials
- `423` - Account locked
- `429` - Rate limit exceeded

#### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout

Logout user and invalidate tokens.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (204 No Content)**

#### GET /auth/me

Get current user information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin1",
  "status": "active",
  "is_active": true,
  "email_verified": true,
  "last_login": "2025-01-29T10:30:00Z",
  "created_at": "2025-01-29T10:30:00Z",
  "permissions": ["users:read", "users:write"]
}
```

#### POST /auth/change-password

Change user password.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

#### POST /auth/forgot-password

Request password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset instructions sent to email"
}
```

#### POST /auth/reset-password

Reset password using reset token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

### User Management Endpoints

#### GET /users

Get list of users (paginated).

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `size` (integer, default: 20, max: 100) - Items per page
- `search` (string) - Search term for name/email
- `role` (string) - Filter by role
- `status` (string) - Filter by status
- `sort` (string) - Sort field (created_at, email, last_login)
- `order` (string) - Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "status": "active",
      "is_active": true,
      "email_verified": true,
      "last_login": "2025-01-29T10:30:00Z",
      "created_at": "2025-01-29T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

#### GET /users/{user_id}

Get specific user by ID.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "status": "active",
  "is_active": true,
  "email_verified": true,
  "last_login": "2025-01-29T10:30:00Z",
  "created_at": "2025-01-29T10:30:00Z",
  "updated_at": "2025-01-29T10:30:00Z"
}
```

#### POST /users

Create new user.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "status": "active",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-01-29T10:30:00Z"
}
```

#### PUT /users/{user_id}

Update user (complete replacement).

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Request Body:**
```json
{
  "email": "updated@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "admin1",
  "status": "active",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "updated@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "admin1",
  "status": "active",
  "is_active": true,
  "updated_at": "2025-01-29T10:30:00Z"
}
```

#### PATCH /users/{user_id}

Partial update of user.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Request Body:**
```json
{
  "first_name": "Updated Name",
  "status": "inactive"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "Updated Name",
  "last_name": "Doe",
  "role": "user",
  "status": "inactive",
  "updated_at": "2025-01-29T10:30:00Z"
}
```

#### DELETE /users/{user_id}

Delete user.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Response (204 No Content)**

#### POST /users/{user_id}/lock

Lock user account.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Request Body:**
```json
{
  "reason": "Security violation",
  "duration_minutes": 60
}
```

**Response (200 OK):**
```json
{
  "message": "User account locked successfully",
  "locked_until": "2025-01-29T11:30:00Z"
}
```

#### POST /users/{user_id}/unlock

Unlock user account.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (UUID) - User identifier

**Response (200 OK):**
```json
{
  "message": "User account unlocked successfully"
}
```

#### POST /users/bulk-actions

Perform bulk actions on multiple users.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "user_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174001"
  ],
  "action": "deactivate",
  "reason": "Bulk deactivation"
}
```

**Response (200 OK):**
```json
{
  "message": "Bulk action completed",
  "affected_users": 2,
  "failed_users": []
}
```

### Admin Management Endpoints

#### GET /admin/users

Get admin users only.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:** Same as `/users` endpoint

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "admin1@example.com",
      "first_name": "Admin",
      "last_name": "One",
      "role": "admin1",
      "status": "active",
      "permissions": ["users:read", "users:write"],
      "last_login": "2025-01-29T10:30:00Z",
      "created_at": "2025-01-29T10:30:00Z"
    }
  ],
  "total": 4,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### POST /admin/users

Create new admin user.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newadmin@example.com",
  "password": "adminpassword123",
  "first_name": "New",
  "last_name": "Admin",
  "role": "admin2",
  "permissions": ["users:read", "users:write"]
}
```

**Response (201 Created):**
```json
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "email": "newadmin@example.com",
  "first_name": "New",
  "last_name": "Admin",
  "role": "admin2",
  "status": "active",
  "permissions": ["users:read", "users:write"],
  "created_at": "2025-01-29T10:30:00Z"
}
```

#### PUT /admin/users/{admin_id}/permissions

Update admin permissions.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `admin_id` (UUID) - Admin user identifier

**Request Body:**
```json
{
  "permissions": [
    "users:read",
    "users:write",
    "users:delete",
    "reports:read"
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Permissions updated successfully",
  "permissions": [
    "users:read",
    "users:write",
    "users:delete",
    "reports:read"
  ]
}
```

### Statistics and Reporting Endpoints

#### GET /stats/overview

Get system overview statistics.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "users": {
    "total": 1250,
    "active": 1180,
    "inactive": 45,
    "locked": 25,
    "new_this_month": 85
  },
  "admins": {
    "total": 4,
    "active": 4,
    "superadmin": 1,
    "admin1": 1,
    "admin2": 1,
    "admin3": 1
  },
  "sessions": {
    "active": 245,
    "total_today": 890,
    "unique_users_today": 456
  },
  "security": {
    "failed_logins_today": 12,
    "locked_accounts_today": 2,
    "password_resets_today": 5
  }
}
```

#### GET /stats/users

Get detailed user statistics.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period` (string) - Time period (day, week, month, year)
- `start_date` (date) - Start date for custom period
- `end_date` (date) - End date for custom period

**Response (200 OK):**
```json
{
  "period": "month",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "registrations": [
    {"date": "2025-01-01", "count": 5},
    {"date": "2025-01-02", "count": 8},
    {"date": "2025-01-03", "count": 12}
  ],
  "logins": [
    {"date": "2025-01-01", "count": 245},
    {"date": "2025-01-02", "count": 289},
    {"date": "2025-01-03", "count": 312}
  ],
  "by_role": {
    "user": 1180,
    "admin1": 1,
    "admin2": 1,
    "admin3": 1,
    "superadmin": 1
  }
}
```

### Audit Log Endpoints

#### GET /audit/logs

Get audit logs.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer) - Page number
- `size` (integer) - Items per page
- `user_id` (UUID) - Filter by user
- `action` (string) - Filter by action
- `resource` (string) - Filter by resource
- `start_date` (datetime) - Start date filter
- `end_date` (datetime) - End date filter

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "log123-456-789",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_email": "admin@example.com",
      "action": "user_created",
      "resource": "users",
      "resource_id": "456e7890-e89b-12d3-a456-426614174001",
      "old_values": null,
      "new_values": {
        "email": "newuser@example.com",
        "role": "user"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-01-29T10:30:00Z"
    }
  ],
  "total": 5000,
  "page": 1,
  "size": 20,
  "pages": 250
}
```

#### GET /audit/logs/export

Export audit logs.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `format` (string) - Export format (csv, json, xlsx)
- `start_date` (datetime) - Start date filter
- `end_date` (datetime) - End date filter
- `user_id` (UUID) - Filter by user
- `action` (string) - Filter by action

**Response (200 OK):**
Returns file download with appropriate content-type.

### Health Check Endpoints

#### GET /health

Basic health check.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-29T10:30:00Z",
  "version": "1.0.0"
}
```

#### GET /health/detailed

Detailed health check including dependencies.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-29T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5,
      "connection_pool": {
        "active": 2,
        "idle": 8,
        "total": 10
      }
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 1
    },
    "disk_space": {
      "status": "healthy",
      "free_gb": 45.2,
      "total_gb": 100.0,
      "usage_percent": 54.8
    },
    "memory": {
      "status": "healthy",
      "free_mb": 2048,
      "total_mb": 8192,
      "usage_percent": 75.0
    }
  }
}
```

## Data Models

### User Model

```json
{
  "id": "UUID",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "avatar_url": "string|null",
  "role": "superadmin|admin1|admin2|admin3|user",
  "status": "active|inactive|locked|pending",
  "is_active": "boolean",
  "email_verified": "boolean",
  "email_verified_at": "datetime|null",
  "last_login": "datetime|null",
  "last_login_ip": "string|null",
  "failed_login_attempts": "integer",
  "locked_at": "datetime|null",
  "locked_until": "datetime|null",
  "password_changed_at": "datetime",
  "password_expires_at": "datetime|null",
  "must_change_password": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "created_by": "UUID|null",
  "updated_by": "UUID|null"
}
```

### Session Model

```json
{
  "id": "UUID",
  "user_id": "UUID",
  "refresh_token": "string",
  "device_info": "object",
  "ip_address": "string",
  "user_agent": "string",
  "is_active": "boolean",
  "expires_at": "datetime",
  "created_at": "datetime",
  "last_used_at": "datetime"
}
```

### Audit Log Model

```json
{
  "id": "UUID",
  "user_id": "UUID|null",
  "action": "string",
  "resource": "string",
  "resource_id": "UUID|null",
  "old_values": "object|null",
  "new_values": "object|null",
  "ip_address": "string|null",
  "user_agent": "string|null",
  "additional_info": "object",
  "created_at": "datetime"
}
```

## Examples

### JavaScript/TypeScript Client

```typescript
class AuthClient {
  private baseURL: string;
  private accessToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    
    // Store refresh token securely
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data;
  }

  async getUsers(page = 1, size = 20) {
    const response = await fetch(
      `${this.baseURL}/users?page=${page}&size=${size}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        await this.refreshToken();
        return this.getUsers(page, size);
      }
      throw new Error('Failed to fetch users');
    }

    return response.json();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    return data;
  }
}

// Usage
const client = new AuthClient('http://localhost:8000/api/v1');

try {
  await client.login('admin@example.com', 'admin123456');
  const users = await client.getUsers();
  console.log('Users:', users);
} catch (error) {
  console.error('Error:', error);
}
```

### Python Client

```python
import requests
from typing import Optional, Dict, Any

class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        
        return data

    def _get_headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("Not authenticated")
        
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_users(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/users",
            params={"page": page, "size": size},
            headers=self._get_headers()
        )
        
        if response.status_code == 401:
            self.refresh_access_token()
            return self.get_users(page, size)
        
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self) -> Dict[str, Any]:
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        
        return data

# Usage
client = AuthClient("http://localhost:8000/api/v1")

try:
    client.login("admin@example.com", "admin123456")
    users = client.get_users()
    print(f"Found {users['total']} users")
except requests.RequestException as e:
    print(f"Error: {e}")
```

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123456"
  }'
```

#### Get Users
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create User
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "New",
    "last_name": "User",
    "role": "user"
  }'
```

## SDKs and Client Libraries

### Official SDKs

- **JavaScript/TypeScript**: `@auth-system/js-sdk`
- **Python**: `auth-system-python`
- **PHP**: `auth-system/php-sdk`
- **Java**: `com.authsystem:java-sdk`

### Installation

#### JavaScript/TypeScript
```bash
npm install @auth-system/js-sdk
```

#### Python
```bash
pip install auth-system-python
```

### Community SDKs

- **Go**: `github.com/community/auth-system-go`
- **Ruby**: `auth-system-ruby` gem
- **C#**: `AuthSystem.NET` NuGet package

---

This API documentation is automatically generated from the OpenAPI specification. For the most up-to-date documentation, visit the interactive docs at `/docs` endpoint.

